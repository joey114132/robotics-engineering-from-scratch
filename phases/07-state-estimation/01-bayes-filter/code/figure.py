# 레슨 07/01 그림: belief 가 날카로워지는 heatmap 과 dead reckoning 대 filter 의 entropy·분산 비교를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("bayes_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
ASSETS = HERE.parent / "assets"


def sharpening():
    steps = 30
    rng = np.random.default_rng(3)
    truth, zs = m.simulate(m.DOORS, 7, [1] * steps, rng)
    bel = m.run(m.DOORS, zs, [1] * steps)
    ent = np.mean([[m.entropy(b) for b in m.run(m.DOORS, m.simulate(m.DOORS, 7, [1] * steps, np.random.default_rng(s))[1], [1] * steps)] for s in range(40)], axis=0)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.1, 1]})
    im = a1.imshow(bel, aspect="auto", cmap="Blues", origin="lower", vmin=0, vmax=1)
    a1.plot(truth, np.arange(1, steps + 1), "o", color=ORANGE, ms=6, label="true cell")
    doors = np.flatnonzero(m.DOORS)
    a1.plot(doors, np.full(len(doors), -1.6), "^", color="black", ms=8, clip_on=False, label="door")
    a1.set_xlabel("corridor cell", labelpad=14)
    a1.set_ylabel("step")
    a1.set_title("Belief starts flat, then locks on")
    a1.grid(False)
    a1.legend(loc="upper left", framealpha=0.95)
    fig.colorbar(im, ax=a1, label="probability", fraction=0.046, pad=0.03)
    a2.plot(ent, color=BLUE)
    a2.axhline(np.log(m.N), color=GREY, ls="--", lw=1.2)
    a2.text(steps * 0.98, np.log(m.N) - 0.12, "uniform: ln 20", ha="right", color=GREY)
    a2.set_xlabel("step")
    a2.set_ylabel("belief entropy (nats), mean of 40 runs")
    a2.set_title("Uncertainty falls as readings arrive")
    a2.set_ylim(0, 3.3)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-belief-sharpening.png", dpi=100)
    plt.close(fig)


def dead_reckoning():
    steps = 120
    moves = [1] * steps
    known = np.zeros(m.N)
    known[7] = 1.0
    ent_dr = [m.entropy(b) for b in m.run(m.DOORS, [0] * steps, moves, use_update=False, bel0=known)]
    ent_f = np.mean([[m.entropy(b) for b in m.run(m.DOORS, m.simulate(m.DOORS, 7, moves, np.random.default_rng(s))[1], moves, bel0=known)] for s in range(40)], axis=0)
    big, n = 400, 60
    bel, var = np.zeros(big), []
    bel[200] = 1.0
    cells = np.arange(big)
    for _ in range(n + 1):
        mu = (bel * cells).sum()
        var.append((bel * (cells - mu) ** 2).sum())
        bel = m.predict(bel, 1)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6))
    a1.plot(ent_dr, color=ORANGE, label="motion only (dead reckoning)")
    a1.plot(ent_f, color=BLUE, label="motion + sensor (filter)")
    a1.set_xlabel("step")
    a1.set_ylabel("belief entropy (nats)")
    a1.set_title("Without the sensor, doubt only grows")
    a1.legend(loc="center right", framealpha=0.95)
    a2.plot(var, "o", color=ORANGE, ms=4, label="simulated variance of the belief")
    a2.plot([0.1 * k for k in range(n + 1)], color=GREY, ls="--", label="derived: 0.1 x steps")
    a2.set_xlabel("step")
    a2.set_ylabel("variance of belief (cells^2)")
    a2.set_title("Each blurred move adds 0.1 cell^2")
    a2.legend(loc="upper left", framealpha=0.95)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-dead-reckoning.png", dpi=100)
    plt.close(fig)


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    sharpening()
    dead_reckoning()
    print("ok")
