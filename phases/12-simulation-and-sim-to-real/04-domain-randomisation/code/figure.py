# 레슨 12/04 그림: 평가 범위에 따른 성공률, 튜닝 범위에 따른 실제 범위 성능을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("dr_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY, GREEN = "#0072B2", "#D55E00", "#555555", "#009E73"
REAL = 0.3  # the uncertainty of the "real" plant in this lesson


def main():
    train = [0.0, 0.1, 0.2, 0.3, 0.45, 0.6]
    gains = {w: m.tune(w, 1 if w == 0 else 60, 1) for w in train}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.4))
    ev = np.linspace(0, 0.6, 7)
    for w, col, lab in ((0.0, ORANGE, "tuned on the nominal plant"), (0.3, BLUE, "tuned across width 0.3"), (0.6, GREEN, "tuned across width 0.6")):
        ax1.plot(ev, [m.evaluate(*gains[w], e, 300, 7)[0] * 100 for e in ev], "o-", color=col, label=lab)
    ax1.axvline(REAL, color=GREY, ls="--")
    ax1.text(REAL + 0.01, 28, "real\nuncertainty", color=GREY, fontsize=12)
    ax1.set_xlabel("randomisation width of the test plants")
    ax1.set_ylabel("success rate (%)")
    ax1.set_ylim(0, 105)
    ax1.set_title("Nominal gains fail on real spread")
    ax1.legend(loc="lower left", fontsize=11)
    res = [m.evaluate(*gains[w], REAL, 300, 7) for w in train]
    ax2.plot(train, [r[1] for r in res], "o-", color=BLUE, label="mean cost (s), failure = 2 s")
    ax2.axvline(REAL, color=GREY, ls="--")
    ax2.set_xlabel("randomisation width used for tuning")
    ax2.set_ylabel("mean cost on width-0.3 plants (s)")
    ax2.set_title("Too narrow fails, too wide is slower")
    ax2.legend(loc="upper right", fontsize=11)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-dr-width.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, {w: (round(g[0], 2), round(g[1], 2)) for w, g in gains.items()}, [(round(r[0], 2), round(r[1], 3)) for r in res])


if __name__ == "__main__":
    main()
