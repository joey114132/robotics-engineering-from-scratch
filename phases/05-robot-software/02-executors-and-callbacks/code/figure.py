# 레슨 05/02 그림: 같은 callback 구성을 스레드 1개와 2개로 돌린 시간선을 위아래로 겹쳐 그린다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("exec_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
CBS = [("timer", 10, 1, "fast", 1), ("slow", 100, 60, "slow", 0)]


def panel(ax, threads, title):
    log = m.simulate(CBS, threads, 1000)
    for n, r, s, e in log:
        if n == "slow":
            ax.broken_barh([(s, e - s)], (-0.35, 0.7), color=ORANGE)
        else:
            ax.plot([r, s], [1, 1], color=GREY, lw=1.2)
            ax.plot(r, 1, "v", color="white", mec=GREY, ms=8)
            ax.plot(s, 1, "o", color=BLUE, ms=6)
    ax.set_xlim(0, 200)
    ax.set_ylim(-0.7, 1.6)
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["slow\n(60 ms)", "timer\n(every 10 ms)"])
    worst = max(m.latencies(log, "timer"))
    ax.set_title(f"{title}: worst timer wait {worst} ms")
    ax.grid(axis="y", alpha=0)


def main():
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 6.2), sharex=True)
    panel(a1, 1, "1 thread")
    panel(a2, 2, "2 threads, separate groups")
    a2.set_xlabel("time (ms).  hollow triangle = timer ready, blue dot = timer starts")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-executor-timeline.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
