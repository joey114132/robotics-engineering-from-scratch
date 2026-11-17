# 레슨 00/05 도해: 점이 같은 거리를 유지한 채 돌아가는 과정과, 같은 방법을 숫자 표로 쓰는 길을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def turn():
    d = Diagram()
    d.title("Turning a point")
    p = d.box("Point\n(1, 0)", col=0, row=0, color="blue")
    a = d.box("Turn a quarter\naround the origin", col=1, row=0, color="purple")
    q = d.box("New point\n(0, 1)", col=2, row=0, color="green")
    d.arrow(p, a)
    d.arrow(a, q)
    d.note("Same distance from the origin", near=q, side="b")
    d.save(OUT / "diagram-turn-point.excalidraw")


def table():
    d = Diagram()
    d.title("The recipe as a table")
    ang = d.box("Angle", col=0, row=0, color="blue")
    tab = d.box("Table of four\nnumbers", col=1, row=0, color="purple")
    mul = d.box("Table @ point", col=1, row=1, color="purple")
    new = d.box("Turned point", col=0, row=1, color="green")
    for s, t in ((ang, tab), (tab, mul), (mul, new)):
        d.arrow(s, t)
    d.note("Four numbers: cos, minus sin, sin, cos", near=tab, side="t")
    d.save(OUT / "diagram-turn-table.excalidraw")


if __name__ == "__main__":
    turn()
    table()
