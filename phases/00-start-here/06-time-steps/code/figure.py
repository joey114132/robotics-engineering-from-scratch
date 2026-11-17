# 레슨 00/06 그림: 떨어지는 공의 실제 낙하 거리와 큰 스텝, 작은 스텝 계산을 비교하고 스텝 크기에 따른 오차를 그린다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lesson_steps_fig", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2))
    t = np.linspace(0, 1, 100)
    a1.plot(t, 0.5 * m.G * t**2, color=GREY, lw=2, label="real fall")
    for dt, col, lab in ((0.5, ORANGE, "big step, 0.5 s"), (0.1, BLUE, "small step, 0.1 s")):
        p = m.positions(m.G, 1.0, dt)
        a1.plot(np.arange(len(p)) * dt, p, "o-", color=col, label=lab)
    a1.set_xlabel("time (s)")
    a1.set_ylabel("distance fallen (m)")
    a1.set_title("Big steps fall too far", fontsize=13)
    a1.legend(fontsize=9)
    a1.grid(alpha=0.3)
    dts = np.array([0.5, 0.25, 0.1, 0.05, 0.025, 0.01])
    err = [m.positions(m.G, 1.0, d)[-1] - m.exact_distance(m.G, 1.0) for d in dts]
    a2.plot(dts, err, "o-", color=ORANGE, lw=2)
    a2.set_xlabel("step size (s)")
    a2.set_ylabel("error after 1 s (m)")
    a2.set_title("Half the step, half the error", fontsize=13)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-step-error.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, "errors", [round(float(e), 3) for e in err])


if __name__ == "__main__":
    main()
