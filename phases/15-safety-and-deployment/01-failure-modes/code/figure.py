# 레슨 15/01 그림: 결함별 관절 응답 여섯 칸과 피해/경보 순위 막대를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("fm_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
ASSETS = HERE.parent / "assets"


def responses():
    fig, axs = plt.subplots(2, 3, figsize=(12, 6.2), sharex=True, sharey=True)
    base = m.simulate("none")
    for ax, f in zip(axs.flat, m.FAULTS):
        run = m.simulate(f)
        s, a = m.metrics(run), m.alarm_time(run)
        ax.plot(base[:, 0], base[:, 1], color=GREY, lw=1.2, ls="--", label="healthy")
        ax.plot(run[:, 0], run[:, 1], color=ORANGE if f != "none" else BLUE, lw=2, label="with fault")
        ax.axhline(m.P["q_lim"], color="k", lw=1)
        ax.axhline(-m.P["q_lim"], color="k", lw=1)
        ax.axhline(m.P["q_ref"], color=BLUE, lw=0.8, ls=":")
        if a is not None:
            ax.axvline(a, color=BLUE, lw=1.2)
        ax.set_title(f"{f}" + (f" (alarm {a:.2f} s)" if a is not None else " (no alarm)"), fontsize=11)
        ax.grid(alpha=0.3)
    axs[0, 0].legend(loc="lower right", fontsize=9)
    for ax in axs[1]:
        ax.set_xlabel("time (s)")
    for ax in axs[:, 0]:
        ax.set_ylabel("joint angle (rad)")
    fig.suptitle("Black lines are the joint limits, the blue vertical line is the first alarm", fontsize=12)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-fault-responses.png", dpi=100)


def ranking():
    rows = [r for r in m.ranked() if r["fault"] != "none"][::-1]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    y = np.arange(len(rows))
    a1.barh(y, [r["final_err"] for r in rows], color=ORANGE)
    a1.set_yticks(y, [r["fault"] for r in rows])
    a1.set_xlabel("error left at the end of the run (rad)")
    a1.set_title("How bad: runaways end 3 rad away")
    a2.barh(y - 0.2, [r["alarm"] if r["alarm"] is not None else np.nan for r in rows], height=0.38, color=BLUE, label="first alarm")
    a2.barh(y + 0.2, [r["t_limit"] if r["t_limit"] is not None else np.nan for r in rows], height=0.38, color=GREY, label="joint reaches limit")
    a2.set_xlabel("time (s)")
    a2.set_title("How detectable: alarm vs time to the limit")
    a2.legend(loc="upper right")
    for ax in (a1, a2):
        ax.grid(alpha=0.3, axis="x")
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-fault-ranking.png", dpi=100)


if __name__ == "__main__":
    responses()
    ranking()
