# 레슨 01/04 그림: 곱의 순서를 바꾸거나 inverse 를 잘못 쓰면 cup 위치가 카메라 yaw 에 따라 얼마나 틀어지는지 그린다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lesson_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def save(fig, name):
    out = HERE.parent / "assets" / name
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


def main():
    yaws = np.radians(np.linspace(0, 180, 181))
    swapped, inverse = [], []
    T_cam_cup = m.make_T(np.eye(3), [0.2, 0.0, 0.5])
    for a in yaws:
        T_base_cam = m.make_T(m.rot_z(a), [0.5, 0.0, 0.4])
        right = (T_base_cam @ T_cam_cup)[:3, 3]
        swapped.append(np.linalg.norm((T_cam_cup @ T_base_cam)[:3, 3] - right))
        inverse.append(np.linalg.norm((m.invert_T(T_base_cam) @ T_cam_cup)[:3, 3] - right))
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot(np.degrees(yaws), swapped, color=ORANGE, lw=2.5, label="factors swapped")
    ax.plot(np.degrees(yaws), inverse, color=BLUE, lw=2.5, label="inverse used by mistake")
    ax.set_xlabel("camera yaw in the base frame (deg)")
    ax.set_ylabel("error of cup position (m)")
    ax.set_title("A wrong product is still a valid pose, but off by up to 1.3 m", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save(fig, "fig-wrong-order-error.png")


if __name__ == "__main__":
    main()
