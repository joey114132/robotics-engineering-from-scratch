# 레슨 00/01 도해: 도를 라디안 자리에 넣은 사고의 경로와 .T 를 빼먹은 회전의 결과를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def units():
    d = Diagram()
    d.title("Degrees fed to np.cos")
    s = d.box("Encoder says\n90 (degrees)", col=0, row=0.5, color="yellow")
    c = d.box("np.cos(90)\nreads radians", col=1, row=0, color="purple")
    r = d.box("-0.448\nshould be 0", col=2, row=0, color="red")
    g = d.box("Guard\njoint_angles()", col=1, row=1, color="green")
    e = d.box("ValueError\nbefore any math", col=2, row=1, color="green")
    d.arrow(s, c, label="no guard")
    d.arrow(c, r)
    d.arrow(s, g, label="guard")
    d.arrow(g, e)
    d.note("silent: no error, no warning", near=r, side="b")
    d.save(OUT / "diagram-degrees-bug.excalidraw")


def shapes():
    d = Diagram()
    d.title("Points are rows")
    p = d.box("Point\n(1, 0, 0)", col=0, row=0.5, color="blue")
    a = d.box("points\n@ R.T", col=1, row=0, color="purple")
    b = d.box("points\n@ R", col=1, row=1, color="purple")
    ok = d.box("(0, 1, 0)\nturned +90", col=2, row=0, color="green")
    bad = d.box("(0, -1, 0)\nturned -90", col=2, row=1, color="red")
    d.arrow(p, a)
    d.arrow(p, b)
    d.arrow(a, ok)
    d.arrow(b, bad)
    d.note("Turn it +90 degrees. Both lines run without an error.", near=bad, side="b")
    d.save(OUT / "diagram-shape-flow.excalidraw")


if __name__ == "__main__":
    units()
    shapes()
