# 레슨 13/03 그림: 시드별 학습 곡선과 기준선 유무에 따른 gradient 추정치의 분산을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pg_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.4))
    for base, color, lab in ((False, ORANGE, "raw return"), (True, BLUE, "with baseline")):
        c = np.array([m.train(np.random.default_rng(s), baseline=base) for s in range(10)])
        x = np.arange(c.shape[1])
        ax1.plot(x, c.mean(0), color=color, lw=2, label=lab)
        ax1.fill_between(x, c.min(0), c.max(0), color=color, alpha=0.18)
    ax1.set(xlabel="training iteration (32 episodes each)", ylabel="mean episode return", title="Same task, same steps: the baseline learns faster", ylim=(34, 46))
    ax1.legend(loc="lower right")
    ax1.grid(alpha=0.3)
    th, rng = np.zeros(2), np.random.default_rng(0)
    bins = np.linspace(-120, 120, 50)
    for base, color, lab in ((False, ORANGE, "raw return"), (True, BLUE, "with baseline")):
        g = np.array([m.grad_estimate(th, rng, 16, base)[0][1] for _ in range(600)])
        ax2.hist(g, bins=bins, color=color, alpha=0.55, label=f"{lab}: std {g.std():.0f}")
        ax2.axvline(g.mean(), color=color, lw=2)
    ax2.set(xlabel="gradient estimate for the bias b (16 episodes)", ylabel="count of 600 estimates", title="Same average, a third of the spread")
    ax2.legend(loc="upper right")
    ax2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-reinforce-baseline.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
