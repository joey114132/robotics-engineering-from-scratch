# 레슨 09/02 도해: RRT 한 번의 확장 루프와 path shortcutting 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("One RRT growth step, repeated")
    a = d.box("Pick a\nrandom spot", 0, 0, "blue")
    b = d.box("Find the nearest\nroute point", 1, 0, "blue")
    c = d.box("Step toward it,\nat most 0.4", 2, 0, "purple")
    e = d.box("Step clear\nof rocks?", 2, 1, "yellow", shape="diamond")
    f = d.box("Yes: keep it\nas a node", 1, 1, "green")
    g = d.box("No: throw\nthe step away", 3, 1, "red")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f, label="yes")
    d.arrow(e, g, label="no")
    d.arrow(f, a, dashed=True, label="next spot")
    d.save(OUT / "diagram-rrt-loop.excalidraw")


def shortcut():
    d = Diagram()
    d.title("Shortcutting: 17.96 long becomes 14.86")
    a = d.box("Wiggly route\nfrom RRT", 0, 0, "red")
    b = d.box("Pick two points\nof the route", 1, 0, "blue")
    c = d.box("Straight line\nclear of rocks?", 1, 1, "yellow", shape="diamond")
    y = d.box("Yes: drop the\npoints between", 2, 1, "green")
    n = d.box("No: keep the\npoints as they are", 0, 1, "gray")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, y, label="yes")
    d.arrow(c, n, label="no")
    d.arrow(y, b, dashed=True, label="try again")
    d.save(OUT / "diagram-shortcut.excalidraw")


if __name__ == "__main__":
    loop()
    shortcut()
