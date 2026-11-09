# 레슨 09/02 도해: RRT 한 번의 확장 루프와 path shortcutting 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(cell=(310, 170))
    d.title("One RRT growth step, repeated")
    a = d.box("Sample a\nrandom point", 0, 0, "blue", w=230)
    b = d.box("Find the nearest\ntree node", 1, 0, "blue", w=230)
    c = d.box("Step toward it,\nat most one step", 2, 0, "purple", w=230)
    e = d.box("Segment\nfree?", 2, 1, "yellow", w=230, shape="diamond", h=110)
    f = d.box("Yes: add\nthe node", 1, 1, "green", w=230)
    g = d.box("No: throw\nthe step away", 3, 1, "red", w=230)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f, label="yes")
    d.arrow(e, g, label="no")
    d.arrow(f, a, dashed=True, label="next sample", label_dx=-60)
    d.save(OUT / "diagram-rrt-loop.excalidraw")


def shortcut():
    d = Diagram(cell=(310, 170))
    d.title("Path shortcutting")
    a = d.box("Raw RRT path\n(wiggly)", 0, 0, "red", w=230)
    b = d.box("Pick two path\npoints at random", 1, 0, "blue", w=230)
    c = d.box("Line between\nthem free?", 2, 0, "yellow", w=250, shape="diamond", h=130)
    y = d.box("Yes: drop the\npoints between", 2, 1, "green", w=230)
    n = d.box("No: keep\nthe path", 3, 1, "gray", w=230)
    r = d.box("Shorter path,\nstill collision free", 0, 1, "green", w=230)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, y, label="yes", label_dx=26)
    d.arrow(c, n, label="no")
    d.arrow(y, r, dashed=True, label="repeat", label_dy=-4)
    d.save(OUT / "diagram-shortcut.excalidraw")


if __name__ == "__main__":
    loop()
    shortcut()
