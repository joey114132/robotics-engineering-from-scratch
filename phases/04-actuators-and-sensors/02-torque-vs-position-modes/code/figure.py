# 레슨 04/02 그림: 외력이 들어올 때 세 모드의 관절 응답과, 요청한 강성 대비 실제로 느껴지는 강성을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("modes_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
STYLE = {"torque": (BLUE, "-", "torque mode, K = 20"), "position": (ORANGE, "-", "position mode (inner kp = 400)"), "admittance": (GREY, "--", "position + admittance, K = 20")}


def main():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.6))
    for mode, (c, ls, lab) in STYLE.items():
        t, q = m.run(mode, K=20.0, push=2.0, T=2.0)
        ax1.plot(t, q * 1e3, ls, color=c, lw=2.4, label=lab)
    ax1.axvline(0.5, color=GREY, lw=1, ls=":")
    ax1.text(0.03, 55, "2 Nm push\nstarts at 0.5 s", fontsize=10, color=GREY)
    ax1.set_xlabel("time (s)")
    ax1.set_ylabel("joint angle (mrad)")
    ax1.set_title("Only torque mode lets K set the give", fontsize=13)
    ax1.legend(fontsize=9, loc="center right")
    ax1.grid(alpha=0.3)

    Ks = np.geomspace(10, 3000, 9)
    for mode, (c, ls, lab) in STYLE.items():
        felt = [m.felt_stiffness(mode, K, T=2.0) for K in Ks]
        ax2.plot(Ks, felt, "o" + ("-" if ls == "-" else "--"), color=c, lw=2, label=lab.split(",")[0])
    ax2.plot(Ks, Ks, ":", color="black", lw=1, label="felt = requested")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("stiffness requested by the outer loop K (Nm/rad)")
    ax2.set_ylabel("stiffness felt when pushed (Nm/rad)")
    ax2.set_title("Position mode ignores the request", fontsize=13)
    ax2.legend(fontsize=9, loc="upper left")
    ax2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-mode-stiffness.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
