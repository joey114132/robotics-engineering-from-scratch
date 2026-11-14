# 레슨 01/02 도해: 팔이 회전하고 한 걸음 나아가는 순서와 두 팔의 reach bounds 를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def walk():
    d = Diagram(numbered=True)
    d.title("Walk the arm: turn, then step")
    base = d.box("Base\nstart at I", 0, 0, "gray", step=1)
    s1 = d.box("Turn Rz(q1)\nat shoulder", 1, 0, "purple", step=2)
    l1 = d.box("Step Tx(l1)\nalong link 1", 2, 0, "purple", step=3)
    s2 = d.box("Turn Rz(q2)\nat elbow", 0, 1, "purple", step=4)
    l2 = d.box("Step Tx(l2)\nalong link 2", 1, 1, "purple", step=5)
    tip = d.box("Tip pose\nthe product", 2, 1, "green", step=6)
    for a, b in ((base, s1), (s1, l1), (l1, s2), (s2, l2), (l2, tip)):
        d.arrow(a, b)
    d.save(OUT / "diagram-fk-walk.excalidraw")


def bounds():
    d = Diagram()
    d.title("Can the tip come back to the base?")
    for row, (links, verdict, shape, color) in enumerate((("Links 1, 1\nsimilar size", "Folds back\nreach 0 to 2", "Full disc", "green"),
                                                         ("Links 3, 1\none is long", "Cannot fold\nreach 2 to 4", "Ring with a hole", "red"))):
        a = d.box(links, 0, row, "blue")
        b = d.box(verdict, 1, row, "purple")
        c = d.box(shape, 2, row, color)
        d.arrow(a, b)
        d.arrow(b, c)
    d.save(OUT / "diagram-reach-bounds.excalidraw")


if __name__ == "__main__":
    walk()
    bounds()
