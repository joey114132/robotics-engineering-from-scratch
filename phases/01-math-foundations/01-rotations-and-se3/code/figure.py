# 레슨 01/01 그림: float32 로 회전을 반복 곱했을 때 drift 가 커지는 모습과 SVD 재직교화의 효과를 그린다
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


def drift(R):
    return float(np.max(np.abs(R.T @ R - np.eye(3))))


def main():
    rng = np.random.default_rng(0)
    steps = 20000
    step = m.rot_x(0.01) @ m.rot_y(0.013) @ m.rot_z(0.007)
    step32 = step.astype(np.float32)
    plain, fixed = np.eye(3, dtype=np.float32), np.eye(3, dtype=np.float32)
    n, d_plain, d_fixed = [], [], []
    for i in range(1, steps + 1):
        plain = plain @ step32
        fixed = m.reorthonormalize(fixed @ step32).astype(np.float32) if i % 100 == 0 else fixed @ step32
        if i % 100 == 0:
            n.append(i)
            d_plain.append(drift(plain.astype(float)))
            d_fixed.append(drift(fixed.astype(float)))
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.plot(n, d_plain, color=ORANGE, lw=2, label="no repair")
    ax.plot(n, d_fixed, color=BLUE, lw=2, label="re-orthonormalise every 100 steps")
    ax.set_yscale("log")
    ax.set_xlabel("number of composed rotations (float32)")
    ax.set_ylabel("drift max|R^T R - I|")
    ax.set_title("Drift grows with every product, a periodic repair resets it", fontsize=13)
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    save(fig, "fig-rotation-drift.png")


if __name__ == "__main__":
    main()
