# 레슨 13/01 그림: 시연 수에 따른 성공률과 정책별 롤아웃 궤적을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("imit_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    counts = [1, 2, 3, 5, 8, 12, 20, 30]
    rates = {"knn": [], "linear": []}
    for n in counts:
        for name, fit in (("knn", m.fit_knn), ("linear", m.fit_linear)):
            rates[name].append([m.success_rate(fit(*m.collect(np.random.default_rng(s), n)), np.random.default_rng(500 + s), n=40) for s in range(8)])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    for name, color, label in (("knn", BLUE, "3-nearest-neighbours"), ("linear", ORANGE, "least squares (linear)")):
        r = np.array(rates[name])
        ax1.plot(counts, r.mean(1), "o-", color=color, label=label)
        ax1.fill_between(counts, r.min(1), r.max(1), color=color, alpha=0.18)
    ax1.axhline(1.0, color=GREY, ls="--", lw=1, label="expert")
    ax1.set(xscale="log", xlabel="number of demonstrations", ylabel="success rate (60 starts)", ylim=(-0.05, 1.08), title="kNN reaches expert level; a line does not")
    ax1.legend(loc="center right")
    ax1.grid(alpha=0.3)
    th = np.linspace(0, 2 * np.pi, 100)
    ax2.fill(m.R_OBST * np.cos(th), m.R_OBST * np.sin(th), color="#bbbbbb")
    ax2.plot(*m.GOAL, "*", color="k", ms=16, label="goal")
    starts = [[-1.3, 0.05], [-1.3, -0.4], [-1.3, 0.5]]
    X10, A10 = m.collect(np.random.default_rng(3), 10)
    for pol, color, ls, lab in ((m.expert, GREY, "--", "expert"), (m.fit_knn(X10, A10), BLUE, "-", "kNN, 10 demos"), (m.fit_linear(X10, A10), ORANGE, "-", "linear, 10 demos")):
        for i, x0 in enumerate(starts):
            xs, _ = m.rollout(pol, x0)
            ax2.plot(xs[:, 0], xs[:, 1], ls, color=color, lw=2, label=lab if i == 0 else None)
    ax2.set(aspect="equal", xlabel="x (m)", ylabel="y (m)", title="Rollouts from three starts", xlim=(-1.5, 1.2), ylim=(-0.9, 0.9))
    ax2.legend(loc="lower left", fontsize=9)
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-imitation-success.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
