# 레슨 00/02 도해: 점이 숫자 두 개가 되는 과정과, 두 점 사이 거리를 구하는 순서
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def point():
    d = Diagram()
    d.title("A point is two numbers")
    o = d.box("Pick a corner\nthe origin", col=0, row=0, color="gray")
    a = d.box("Count across\n2 metres", col=1, row=0, color="blue")
    u = d.box("Count up\n1.5 metres", col=2, row=0, color="blue")
    p = d.box("The point\n(2, 1.5)", col=2, row=1, color="green")
    d.arrow(o, a)
    d.arrow(a, u)
    d.arrow(u, p)
    d.note("a new corner gives new numbers", near=o, side="b")
    d.save(OUT / "diagram-point-from-origin.excalidraw")


def distance():
    d = Diagram()
    d.title("How far apart are two points?")
    a = d.box("Point A\nPoint B", col=0, row=0, color="blue")
    s = d.box("Across gap and\nup gap", col=1, row=0, color="purple")
    h = d.box("Diagonal\nmath.hypot", col=2, row=0, color="purple")
    r = d.box("Distance\n2.5 m", col=2, row=1, color="green")
    d.arrow(a, s, label="subtract")
    d.arrow(s, h)
    d.arrow(h, r)
    d.note("same answer from any corner", near=r, side="l")
    d.save(OUT / "diagram-distance-recipe.excalidraw")


if __name__ == "__main__":
    point()
    distance()
