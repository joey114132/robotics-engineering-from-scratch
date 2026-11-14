# 레슨 11/03 도해: 손끝 접촉에서 friction cone wrench 를 거쳐 force closure 판정까지의 흐름과, 마찰 유무에 따른 비틀림 저항을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram(numbered=True)
    d.title("From fingertips to a closure test")
    a = d.box("Fingertip point\n+ inward normal", 0, 0, "blue", step=1)
    b = d.box("Friction cone\nedges n +- mu t", 1, 0, "yellow", step=2)
    c = d.box("Edges as wrenches\n(fx, fy, torque)", 2, 0, "purple", step=3)
    e = d.box("Convex hull of\nall wrenches", 2, 1, "gray", step=4)
    f = d.box("Origin inside\nthe hull?", 1, 1, "red", shape="diamond", step=5)
    g = d.box("Closure: the box\nresists any load", 0, 1, "green", step=6)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.arrow(f, g, label="yes")
    d.note("Radius of the biggest ball around the origin = quality epsilon.", near=g, side="b")
    d.save(OUT / "diagram-closure-pipeline.excalidraw")


def cases():
    d = Diagram()
    d.title("Why friction decides closure")
    a = d.box("Two fingertips\npinch the box", 0, 0.5, "gray")
    b = d.box("mu = 0\n2 wrenches in a line", 1, 0, "red")
    c = d.box("mu > 0\n4 wrenches", 1, 1, "green")
    r = d.box("A twist\ngoes unresisted", 2, 0, "red")
    s = d.box("Force and torque\nboth resisted", 2, 1, "green")
    for u, v in ((a, b), (a, c), (b, r), (c, s)):
        d.arrow(u, v)
    d.save(OUT / "diagram-friction-needed.excalidraw")


if __name__ == "__main__":
    pipeline()
    cases()
