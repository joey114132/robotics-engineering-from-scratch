# 레슨 06/04 그림: 회전축이 퍼진 정도에 따른 손-눈 보정 오차와 관측 가능성 비율을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("handeye_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

X = m.make_T(m.rodrigues(np.array([0.3, -0.5, 0.8])), [0.05, 0.03, 0.08])
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    spreads = np.array([0.0, 2, 5, 10, 20, 40, 60, 90])
    rot, tr, ratio = [], [], []
    for sp in spreads:
        r = []
        for seed in range(60):
            Xe, s = m.solve_hand_eye(*m.make_motions(X, 12, sp, 0.2, 0.001, seed))
            r.append((*m.pose_error(Xe, X), s[1] / s[0]))
        r = np.array(r)
        rot.append(np.median(r[:, 0]))
        tr.append(np.median(r[:, 1]) * 1000)
        ratio.append(np.median(r[:, 2]))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    x = np.maximum(spreads, 1.0)  # plot spread 0 at 1 deg on the log axis and label it
    ax1.plot(x, rot, "o-", color=BLUE, lw=2.2, label="rotation error (deg)")
    ax1.plot(x, tr, "s-", color=ORANGE, lw=2.2, label="translation error (mm)")
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xticks([1, 2, 5, 10, 20, 40, 90])
    ax1.set_xticklabels(["0", "2", "5", "10", "20", "40", "90"])
    ax1.set_xlabel("spread of rotation axes around z (deg)")
    ax1.set_ylabel("median error over 60 noisy runs")
    ax1.set_title("One rotation axis: the answer is unusable")
    ax1.legend(loc="upper right")
    ax1.grid(alpha=0.3, which="both")
    ax2.plot(x, np.maximum(ratio, 1e-9), "o-", color=GREY, lw=2.2)
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xticks([1, 2, 5, 10, 20, 40, 90])
    ax2.set_xticklabels(["0", "2", "5", "10", "20", "40", "90"])
    ax2.set_xlabel("spread of rotation axes around z (deg)")
    ax2.set_ylabel("second / first singular value")
    ax2.text(1.1, 3e-9, "a ratio of exactly 0 is drawn at 1e-9", fontsize=9, color=GREY)
    ax2.set_title("The ratio tells you before the robot moves")
    ax2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-handeye-spread.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, [round(v, 3) for v in rot], [round(v, 1) for v in tr], [f"{v:.1e}" for v in ratio])


if __name__ == "__main__":
    main()
