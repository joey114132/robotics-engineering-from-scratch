# 레슨 05/03: 고정 주기 loop 를 시뮬레이션해 period jitter, deadline miss, 최악 지연을 잰다
import numpy as np


def simulate(n, T=1e-3, work=2e-4, lat_scale=2e-5, spike_p=0.002, relative=False, seed=0):
    """Return start and done times of n loop iterations.

    Wake-up latency is exponential (typical scheduler noise) plus rare spikes of 0.5 to 1.5 periods
    (a stand-in for preemption). relative=True sleeps T after the work; otherwise it sleeps until i*T.
    """
    rng = np.random.default_rng(seed)
    lat = rng.exponential(lat_scale, n)
    spike = rng.random(n) < spike_p
    lat[spike] += rng.uniform(0.5 * T, 1.5 * T, spike.sum())
    s, d = np.empty(n), np.empty(n)
    done = 0.0
    for i in range(n):
        wake = (done + T if relative else i * T) + lat[i]
        s[i] = max(wake, done)  # a late iteration cannot start before the previous one is done
        d[i] = done = s[i] + work
    return s, d


def stats(s, d, T):
    """Period jitter is period - T. A miss is an iteration that finishes after its next deadline."""
    jit = np.diff(s) - T
    return dict(mean_period=float(np.mean(np.diff(s))), mean_jitter=float(jit.mean()), std=float(jit.std()),
                p99=float(np.percentile(np.abs(jit), 99)), worst=float(np.abs(jit).max()),
                misses=int(np.sum(d[:-1] > (np.arange(len(d) - 1) + 1) * T)))


if __name__ == "__main__":
    s, d = simulate(5000, spike_p=0.003)
    for k, v in stats(s, d, 1e-3).items():
        print(f"{k:12s} {v * 1e6 if k != 'misses' else v:10.1f}" + ("" if k == "misses" else " us"))
