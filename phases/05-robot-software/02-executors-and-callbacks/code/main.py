# 레슨 05/02: 1 ms 단위로 시간을 흘리는 executor 시뮬레이션. 스레드 수와 mutually exclusive callback group 을 모델링한다
def simulate(callbacks, threads, horizon):
    """callbacks: (name, period, duration, group, first_release) in ms. Returns (name, release, start, end) per job.

    One job per released callback waits in a FIFO. A free thread takes the oldest job whose group is idle.
    group None means reentrant: it never blocks itself. Mutually exclusive groups run one job at a time.
    """
    pending, running, log = [], [], []  # running: (end, group)
    for t in range(horizon):
        for name, period, dur, group, first in callbacks:
            if t >= first and (t - first) % period == 0:
                pending.append((name, t, dur, group))
        running = [r for r in running if r[0] > t]
        while len(running) < threads:
            busy = {g for _, g in running if g is not None}
            job = next((j for j in pending if j[3] is None or j[3] not in busy), None)
            if job is None:
                break
            pending.remove(job)
            running.append((t + job[2], job[3]))
            log.append((job[0], job[1], t, t + job[2]))
    return log


def latencies(log, name):
    """Wait between release and start, per job of one callback."""
    return [s - r for n, r, s, _ in log if n == name]


def late_ticks(log, name, period):
    """Jobs that started at least one whole period after they were released."""
    return sum(x >= period for x in latencies(log, name))


if __name__ == "__main__":
    cbs = [("timer", 10, 1, "fast", 1), ("slow", 100, 60, "slow", 0)]
    for n in (1, 2):
        print(n, "thread(s): worst timer wait", max(latencies(simulate(cbs, n, 1000), "timer")), "ms")
