# 레슨 13/06 그림: 평균 회귀의 충돌, 표본 궤적의 부채꼴, 청크 길이에 따른 떨림을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("chunks_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
START = np.array([-1.0, 0.0])


def scene(ax, P, title):
    ax.add_patch(plt.Circle((0, 0), m.R_OBST, color=GREY, alpha=0.8))
    for p in P:
        ax.plot(p[:, 0], p[:, 1], color="#bbbbbb", lw=1)
    ax.plot(*START, "ks")
    ax.plot(*m.GOAL, "k*", ms=12)
    ax.set_aspect("equal")
    ax.set_xlim(-1.15, 1.45)
    ax.set_ylim(-0.8, 0.8)
    ax.set_title(title, fontsize=11)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")


def main():
    P, A = m.demos(6, np.random.default_rng(0))
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1, 1, 1]})
    scene(a1, P, "Mean regression: straight into the disc")
    path = m.rollout_mean(m.mean_policy(P, A), START)
    a1.plot(path[:, 0], path[:, 1], color=ORANGE, lw=3, label="mean policy")
    a1.legend(loc="lower right")
    scene(a2, P, "Chunk sampler: 40 rollouts, each commits")
    for s in range(40):
        p = m.rollout_chunks(P, A, START, 8, 4, np.random.default_rng(s))
        a2.plot(p[:, 0], p[:, 1], color=BLUE, lw=1.4, alpha=0.5)
    Hs = [1, 2, 4, 8, 16]
    jit, ok = [], []
    for H in Hs:
        runs = [m.rollout_chunks(P, A, START, H, H // 2, np.random.default_rng(s)) for s in range(60)]
        jit.append(np.mean([m.jitter(r) for r in runs]))
        ok.append(100 * np.mean([m.clear(r) for r in runs]))
    a3.plot(Hs, jit, "o-", color=BLUE, label="action jitter")
    a3.set_xscale("log", base=2)
    a3.set_xticks(Hs)
    a3.set_xticklabels(Hs)
    a3.set_xlabel("chunk length H (steps), overlap H/2")
    a3.set_ylabel("action jitter (m per step^2)", color=BLUE)
    a3.set_ylim(0, max(jit) * 1.15)
    a3b = a3.twinx()
    a3b.plot(Hs, ok, "s--", color=ORANGE, label="rollouts clear of disc")
    a3b.set_ylim(90, 101)
    a3b.set_ylabel("rollouts clear of disc (%)", color=ORANGE)
    a3.set_title("Longer chunks: smoother and safer", fontsize=11)
    a3.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-chunk-fan.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, [round(j, 4) for j in jit], ok)


if __name__ == "__main__":
    main()
