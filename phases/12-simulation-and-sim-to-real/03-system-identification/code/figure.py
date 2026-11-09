# 레슨 12/03 그림: 맞춘 모델과 데이터, 느린 궤적의 실패, 가진 크기에 따른 파라미터 오차를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("id_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY, GREEN = "#0072B2", "#D55E00", "#555555", "#009E73"


def main():
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.8))
    ax1, ax2, ax3 = axes
    rich = m.record(m.experiment(1.0), 0.01, 1e-4, 1)
    est = m.fit(rich)[0]
    y, y_hat = m.predict(est, rich)
    t = np.arange(len(y)) * 25 * (rich[1, 0] - rich[0, 0])
    sl = t < 6
    ax1.plot(t[sl], y[sl], ".", color=GREY, label="data")
    ax1.plot(t[sl], y_hat[sl], "-", color=BLUE, label="fitted model")
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("speed change per 50 ms (rad/s)")
    ax1.set_title("Rich run: fit follows the data")
    ax1.set_ylim(-1.2, 1.8)
    ax1.legend(loc="upper right", fontsize=11, ncol=2)
    names = ("J", "b", "c")
    for a, col, lab in ((0.0, ORANGE, "one slow run"), (1.0, BLUE, "rich run")):
        e, _, _ = m.fit(m.record(m.experiment(a), 0.01, 1e-4, 1))
        e_slow = e if a == 0.0 else e_slow
        ax2.bar(np.arange(3) + (0.2 if a else -0.2), [e[k] / m.TRUE[k] for k in names], 0.4, color=col, label=lab)
    ax2.axhline(1, color=GREY, ls="--")
    ax2.set_xticks(range(3), names)
    ax2.set_ylabel("estimate / true value")
    ax2.set_ylim(-24, 6)
    ax2.set_title("Slow run: b and c blow up")
    ax2.legend(loc="lower left", fontsize=11)
    ax2.text(2.0, -10, "b: %.0fx true" % (e_slow["b"] / m.TRUE["b"]), ha="center", fontsize=11)
    amps = [0.0, 0.05, 0.1, 0.2, 0.4, 0.8, 1.5]
    errs = [m.excitation_error(a, 0.01, 1e-4, 4) for a in amps]
    for k, col in zip(names, (GREY, ORANGE, BLUE)):
        ax3.semilogy(amps, [max(e[k], 1e-3) for e in errs], "o-", color=col, label=k)
    ax3.set_xlabel("excitation size a (rad/s)")
    ax3.set_ylabel("relative parameter error")
    ax3.set_title("More excitation helps")
    ax3.legend(loc="upper right", fontsize=11)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-id-fit.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, [round(e["b"], 3) for e in errs])


if __name__ == "__main__":
    main()
