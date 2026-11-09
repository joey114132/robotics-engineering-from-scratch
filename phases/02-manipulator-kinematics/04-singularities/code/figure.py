# 레슨 02/04 그림: elbow 각이 0 에 가까워질 때 joint 속도가 폭주하는 모습과 damping 의 대가인 tip 속도 오차를 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("sing_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
L, V = (0.5, 0.4), np.array([0.1, 0.0])


def main():
    q2 = np.logspace(np.log10(0.003), np.log10(1.5), 300)
    Js = [m.jacobian([0.0, a], L) for a in q2]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.4))
    plain = [np.linalg.norm(m.solve(J, V, 0.0)) for J in Js]
    ax1.loglog(q2, plain, color=ORANGE, lw=2.5, label="plain inverse")
    for lam, ls in ((0.05, "-"), (0.15, "--")):
        ax1.loglog(q2, [np.linalg.norm(m.solve(J, V, lam)) for J in Js], ls, color=BLUE, lw=2.2, label=f"damped, lam = {lam}")
        ax1.axhline(np.linalg.norm(V) / (2 * lam), color=GREY, lw=0.8, ls=":")
    ax1.text(0.0035, 1.25, "bound |v| / (2 lam)", fontsize=10, color=GREY)
    ax1.set_xlabel("elbow angle q2 (rad), 0 = arm fully straight")
    ax1.set_ylabel("joint speed norm |qd| (rad/s)")
    ax1.set_title("Asking for 0.1 m/s outward: joint speed blows up", fontsize=13)
    ax1.legend(loc="upper right", fontsize=10)
    ax1.grid(alpha=0.3, which="both")
    for lam, ls in ((0.05, "-"), (0.15, "--")):
        e = [np.linalg.norm(J @ m.solve(J, V, lam) - V) / np.linalg.norm(V) * 100 for J in Js]
        ax2.semilogx(q2, e, ls, color=BLUE, lw=2.2, label=f"damped, lam = {lam}")
    ax2.semilogx(q2, [0] * len(q2), color=ORANGE, lw=2.5, label="plain inverse (exact, but unusable)")
    ax2.set_xlabel("elbow angle q2 (rad), 0 = arm fully straight")
    ax2.set_ylabel("tip velocity error (% of command)")
    ax2.set_title("Damping trades tip accuracy for bounded speed", fontsize=13)
    ax2.legend(loc="center left", bbox_to_anchor=(0.02, 0.3), fontsize=10)
    ax2.grid(alpha=0.3, which="both")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-speed-blowup.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
