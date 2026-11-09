# 레슨 11/03 도해: 접촉 마찰 원뿔에서 wrench 를 거쳐 force closure 판정까지의 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram()
    d.title("From contacts to a closure test")
    a = d.box("Contact point\n+ inward normal", 0, 0, "blue")
    b = d.box("Friction cone\nedges n +- mu t", 1, 0, "yellow")
    c = d.box("Wrench per edge\n(fx, fy, torque)", 2, 0, "purple")
    e = d.box("Convex hull of\nall wrenches", 3, 0, "gray")
    f = d.box("Origin inside\nthe hull?", 3, 1, "red", shape="diamond", w=230, h=110)
    g = d.box("Closure: any load\ncan be resisted", 2, 1, "green", w=240)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.arrow(f, g, label="yes")
    d.note("Radius of the biggest ball around the origin = quality epsilon.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=20)
    d.save(OUT / "diagram-closure-pipeline.excalidraw")


def cases():
    d = Diagram(cell=(330, 170))
    d.title("Why friction decides closure")
    a = d.box("Two opposite\ncontacts", 0, 0.5, "gray", w=220)
    b = d.box("mu = 0\nonly 2 wrenches", 1, 0, "red", w=240)
    c = d.box("mu > 0\n4 wrenches", 1, 1, "green", w=240)
    r = d.box("Cannot resist\na twist", 2, 0, "red", w=230)
    s = d.box("Resists force\nand torque", 2, 1, "green", w=230)
    for u, v in ((a, b), (a, c), (b, r), (c, s)):
        d.arrow(u, v)
    d.save(OUT / "diagram-friction-needed.excalidraw")


if __name__ == "__main__":
    pipeline()
    cases()
