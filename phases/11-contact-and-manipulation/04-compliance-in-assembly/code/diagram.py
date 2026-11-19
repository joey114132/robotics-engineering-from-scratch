# 레슨 11/04 도해: 딱딱한 손목은 구멍이 좁아져도 기울기를 고집해 peg 가 wedge 되고 jam 이 걸리는 연쇄와, 부드러운 손목이 비켜 주는 연쇄를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def jam():
    d = Diagram(numbered=True)
    d.title("How a stiff wrist jams the peg")
    a = d.box("Peg is 1 mm off\nthe hole centre", 0, 0, "yellow", step=1)
    b = d.box("Stiff wrist holds\nthe peg top at 1 mm", 1, 0, "purple", step=2)
    c = d.box("Deeper, the hole\nallows less lean", 2, 0, "red", step=3)
    e = d.box("Edge catches the\npeg, walls squeeze", 2, 1, "red", step=4)
    f = d.box("JAM at 34.6 mm\npush is still 5 N", 1, 1, "red", step=5)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.note("The wall force is what feeds the friction.", near=f, side="b")
    d.save(OUT / "diagram-jam-chain.excalidraw")


def comply():
    d = Diagram()
    d.title("Same 1 mm offset, same 5 N push")
    a = d.box("Wrist holds\nthe peg", 1, 0, "yellow")   # a tree: one branch per wrist, so each arrow meets the middle of a side
    b = d.box("Stiff wrist\n1e5 N/m", 0, 1, "red")
    c = d.box("Soft wrist\n1e3 N/m", 2, 1, "green")
    r = d.box("Walls pushed with\nup to 8.2 N: JAM", 0, 2, "red")
    s = d.box("Walls pushed with\nup to 1.2 N: goes in", 2, 2, "green")
    for u, v in ((a, b), (a, c), (b, r), (c, s)):
        d.arrow(u, v)
    d.save(OUT / "diagram-comply.excalidraw")


if __name__ == "__main__":
    jam()
    comply()
