# 레슨 02/02 도해: IK 가 삼각형 하나로 풀리는 순서와, 도달 가능 여부에 따라 갈리는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def triangle():
    d = Diagram(cell=(310, 150))
    d.title("IK is one triangle")
    a = d.box("Target (x, y)", 0, 0.5, "blue", w=200)
    b = d.box("Distance r\nfrom the base", 1, 0.5, "gray", w=200)
    c = d.box("Law of cosines\ngives cos q2", 2, 0.5, "purple", w=210)
    e = d.box("q2 = +acos or -acos\n(two elbows)", 3, 0, "yellow", w=230)
    f = d.box("q1 from the angle\nto the target", 3, 1, "purple", w=230)
    for s, t in ((a, b), (b, c), (c, e), (c, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-triangle.excalidraw")


def decision():
    d = Diagram(cell=(310, 150))
    d.title("Check reach first, then check the answer")
    a = d.box("Target\nat distance r", 0, 0.5, "blue", w=190)
    b = d.box("|L1 - L2| <= r\n<= L1 + L2 ?", 1, 0.5, "yellow", w=270, shape="diamond", h=140)
    no = d.box("No: refuse\n(raise an error)", 2, 1.2, "red", w=220)
    yes = d.box("Yes: two answers\nelbow-up, elbow-down", 2, 0, "purple", w=240)
    fk = d.box("Run FK on the answer\nmust land on the target", 3, 0, "green", w=250)
    for s, t, lab in ((a, b, None), (b, no, "no"), (b, yes, "yes"), (yes, fk, None)):
        d.arrow(s, t, label=lab)
    d.save(OUT / "diagram-decision.excalidraw")


if __name__ == "__main__":
    triangle()
    decision()
