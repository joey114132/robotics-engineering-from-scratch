# 레슨 00/01 도해: 도를 라디안 자리에 넣은 사고의 경로와 점 배열 곱셈의 shape 흐름을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def units():
    d = Diagram()
    d.title("Degrees fed to np.cos")
    a = d.box("Sensor value\n90 (degrees)", 0, 0.5, "yellow")
    b = d.box("np.cos(90)\nreads radians", 1, 0.5, "purple")
    c = d.box("-0.448\nshould be 0", 2, 0, "red")
    g = d.box("Guard: joint_angles()\nrefuses q > 2 pi", 2, 1, "green", w=260)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(b, g, dashed=True)
    d.note("numpy never complains. The unit lives in your head.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-degrees-bug.excalidraw")


def shapes():
    d = Diagram()
    d.title("Points are rows")
    p = d.box("points\n(N, 3)", 0, 0, "blue")
    r = d.box("R\n(3, 3)", 0, 1, "blue")
    ok = d.box("points @ R.T\n(N, 3)", 1.2, 0.5, "purple")
    good = d.box("rotated by +theta", 2.4, 0, "green", w=240)
    bad = d.box("points @ R\nrotated by -theta", 2.4, 1, "red", w=240)
    d.arrow(p, ok)
    d.arrow(r, ok)
    d.arrow(ok, good)
    d.arrow(r, bad, dashed=True, label="forgot .T")
    d.save(OUT / "diagram-shape-flow.excalidraw")


if __name__ == "__main__":
    units()
    shapes()
