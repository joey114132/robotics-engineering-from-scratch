# 레슨 00/02 그림: 바닥 위 세 점의 경로와, 두 점 사이 직선 거리, 원점을 바꿔도 거리가 같은 것을 그린다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("points_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    A, B, C = m.ROUTE
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2))
    a1.plot([A[0], B[0], C[0]], [A[1], B[1], C[1]], "o-", color=BLUE, lw=2.5, ms=9, label=f"via B: {m.path_length(m.ROUTE):.1f} m")
    a1.plot([A[0], C[0]], [A[1], C[1]], "--", color=ORANGE, lw=2, label=f"straight: {m.distance(A, C):.1f} m")
    for name, p in zip("ABC", m.ROUTE):
        a1.annotate(f"{name} {p}", p, textcoords="offset points", xytext=(8, 8), fontsize=11)
    a1.set_xlim(-0.4, 2.8)
    a1.set_ylim(-0.4, 2.0)
    a1.set_xlabel("across (m)")
    a1.set_ylabel("up (m)")
    a1.set_title("Cutting the corner saves one metre", fontsize=13)
    a1.legend(loc="upper left", fontsize=10)
    a1.grid(alpha=0.3)
    a1.set_aspect("equal")
    origins = {"room corner": (0, 0), "point B": B, "point C": C}
    xs = range(len(origins))
    dists = [m.distance(m.measured_from(A, o), m.measured_from(C, o)) for o in origins.values()]
    a2.bar(xs, dists, color=BLUE, width=0.5)
    a2.set_xticks(list(xs))
    a2.set_xticklabels(list(origins))
    a2.set_ylim(0, 3.2)
    for x, v in zip(xs, dists):
        a2.text(x, v + 0.08, f"{v:.1f} m", ha="center", fontsize=11)
    a2.set_xlabel("origin used to count the numbers")
    a2.set_ylabel("distance from A to C (m)")
    a2.set_title("Move the origin, the distance stays", fontsize=13)
    a2.grid(alpha=0.3, axis="y")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-route-and-origin.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, "distances", dists)


if __name__ == "__main__":
    main()
