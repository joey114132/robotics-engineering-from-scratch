# 레슨 14/02 그림: 링, 완전, 끊어진 그래프의 상태 수렴, 그리고 측정한 수렴 속도 대 eps*lambda2
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("cons_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
ASSETS = HERE.parent / "assets"
X0 = np.array([4.0, -1.0, 2.0, 7.0, 0.0, 3.0, -5.0, 1.0])


def path(n):
    A = np.zeros((n, n))
    for i in range(n - 1):
        A[i, i + 1] = A[i + 1, i] = 1
    return A


def star(n):
    A = np.zeros((n, n))
    A[0, 1:] = A[1:, 0] = 1
    return A


def measured_rate(A, eps):
    d = np.linalg.norm((t := m.run(np.random.default_rng(len(A)).normal(size=len(A)), A, eps, 600)) - t.mean(axis=1, keepdims=True), axis=1)
    k = int(np.argmax(d < 1e-6)) if (d < 1e-6).any() else 600
    k0 = k // 2
    return 1 - (d[k] / d[k0]) ** (1 / (k - k0))


def main():
    two = np.zeros((8, 8))
    two[:4, :4], two[4:, 4:] = m.complete(4), m.complete(4)
    fig, axs = plt.subplots(1, 3, figsize=(14, 5), sharey=True)
    for ax, (name, A) in zip(axs, (("Ring", m.ring(8)), ("Complete", m.complete(8)), ("Two groups", two))):
        traj = m.run(X0, A, 0.05, 120)
        ax.plot(traj, lw=1.8)
        ax.axhline(X0.mean(), color="black", ls="--", lw=1)
        ax.set_title(f"{name}: lambda2 = {abs(m.lambda2(m.laplacian(A))):.2f}")
        ax.set_xlabel("step")
    axs[0].set_ylabel("robot state x_i")
    axs[0].text(60, X0.mean() + 0.4, "initial average", fontsize=12)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-consensus-states.png", dpi=100)

    fig, ax = plt.subplots(figsize=(8, 6.4))
    pts = []
    for fam, gen, ns, mark in (("ring", m.ring, range(4, 13), "o"), ("complete", m.complete, range(3, 9), "s"), ("path", path, range(4, 11), "^"), ("star", star, range(4, 10), "D")):
        xs, ys = [], []
        for n in ns:
            A = gen(n)
            eps = 0.4 / A.sum(axis=1).max()
            xs.append(eps * m.lambda2(m.laplacian(A)))
            ys.append(measured_rate(A, eps))
        ax.plot(xs, ys, mark, ms=9, label=fam)
        pts += list(zip(xs, ys))
    lim = [min(p[0] for p in pts) * 0.7, max(p[0] for p in pts) * 1.4]
    ax.plot(lim, lim, "-", color=GREY, lw=1.5, label="y = x")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("eps * lambda2 (per step)")
    ax.set_ylabel("measured decay rate 1 - ratio (per step)")
    ax.set_title("Measured speed equals eps * lambda2")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-rate-vs-lambda2.png", dpi=100)
    print(max(abs(y / x - 1) for x, y in pts))


if __name__ == "__main__":
    main()
