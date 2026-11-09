# 레슨 01/02 도해: 순기구학 곱의 순서와 reach bounds 의 두 경우를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def walk():
    d = Diagram()
    d.title("Walk the chain: rotate, then step")
    b = d.box("Base\nT = I", 0, 0, "gray", w=200)
    j1 = d.box("Joint 1 and link 1\nRz(q1) then Tx(l1)", 1, 0, "purple", w=260)
    j2 = d.box("Joint 2 and link 2\nRz(q2) then Tx(l2)", 2, 0, "purple", w=260)
    t = d.box("Tip pose\nthe ordered product", 3, 0, "green", w=240)
    for s, e in ((b, j1), (j1, j2), (j2, t)):
        d.arrow(s, e)
    d.note("Swap two factors and the tip lands somewhere else.", d.margin, d.margin + 60 + d.ch - 20, size=20)
    d.save(OUT / "diagram-fk-walk.excalidraw")


def bounds():
    d = Diagram(cell=(340, 170))
    d.title("Can the tip come back to the base?")
    c = d.box("Compare the longest\nlink with the others", 0, 0.5, "gray", w=260)
    ok = d.box("Longest <= sum of others\nmin reach = 0", 1, 0, "green", w=280)
    hole = d.box("Longest > sum of others\nmin reach = 2L - sum", 1, 1, "red", w=280)
    r1 = d.box("Disc of reach", 2, 0, "green", w=200)
    r2 = d.box("Ring with a hole", 2, 1, "red", w=200)
    for s, e in ((c, ok), (c, hole), (ok, r1), (hole, r2)):
        d.arrow(s, e)
    d.save(OUT / "diagram-reach-bounds.excalidraw")


if __name__ == "__main__":
    walk()
    bounds()
