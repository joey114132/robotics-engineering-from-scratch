# 레슨 13/02 그림: 호라이즌에 따른 행동 오차 증가와 DAgger 라운드별 성공률을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("clone_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
SEEDS, ROUNDS = range(6), range(0, 6)


def main():
    curves = {0: [], 4: []}
    succ = {r: [] for r in ROUNDS}
    for s in SEEDS:
        for r in ROUNDS:
            pol, X = m.dagger(np.random.default_rng(s), 4, rounds=r)
            if r in curves:
                curves[r].append(m.drift_curves(pol, X, np.random.default_rng(70 + s), n=30)[0])
            succ[r].append(m.noisy_success(pol, np.random.default_rng(90 + s), n=30))
    expert_rate = np.mean([m.noisy_success(m.expert, np.random.default_rng(300 + s), n=30) for s in SEEDS])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.4))
    t = np.arange(120)
    for r, color, lab in ((0, ORANGE, "plain cloning (4 demos)"), (4, BLUE, "after 4 DAgger rounds")):
        c = np.array(curves[r])
        ax1.plot(t, c.mean(0), color=color, lw=2, label=lab)
        ax1.fill_between(t, c.min(0), c.max(0), color=color, alpha=0.15)
    ax1.set(xlabel="time step (dt = 0.05 s)", ylabel="action error vs expert (|a| units)", title="Cloning error grows after the first steps")
    ax1.legend(loc="upper left")
    ax1.grid(alpha=0.3)
    mean = [np.mean(succ[r]) for r in ROUNDS]
    ax2.plot(list(ROUNDS), mean, "o-", color=BLUE, lw=2, label="cloned policy")
    ax2.fill_between(list(ROUNDS), [min(succ[r]) for r in ROUNDS], [max(succ[r]) for r in ROUNDS], color=BLUE, alpha=0.15)
    ax2.axhline(expert_rate, color=GREY, ls="--", label="expert under the same noise")
    ax2.set(xlabel="DAgger rounds (5 labelled rollouts each)", ylabel="success rate with action noise", ylim=(0, 1.05), title="Recovery data closes the gap")
    ax2.legend(loc="lower right")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-cloning-drift.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, [round(x, 2) for x in mean], round(expert_rate, 2))


if __name__ == "__main__":
    main()
