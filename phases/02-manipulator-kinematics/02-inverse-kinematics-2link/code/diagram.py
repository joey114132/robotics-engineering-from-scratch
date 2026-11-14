# 레슨 02/02 도해: IK 가 삼각형 하나로 풀리는 순서와, 도달 가능 여부에 따라 갈리는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def triangle():
    d = Diagram(numbered=True)
    d.title("IK is one triangle")
    a = d.box("Ball at (x, y),\nr from the base", col=0, row=0, color="blue")
    b = d.box("Law of cosines\ngives cos q2", col=0, row=1, color="purple")
    c = d.box("q2 is +acos or -acos:\ntwo elbows", col=0, row=2, color="yellow")
    e = d.box("Then q1 from the\nangle to the ball", col=0, row=3, color="purple")
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.save(OUT / "diagram-triangle.excalidraw")


def decision():
    d = Diagram()
    d.title("Check reach first, then check the answer")
    a = d.box("Ball at\ndistance r", col=0, row=0.5, color="blue")
    b = d.box("r inside\nthe band?", col=1, row=0.5, color="yellow", shape="diamond")
    yes = d.box("Two answers:\nelbow up, down", col=2, row=0, color="purple")
    no = d.box("Refuse:\nraise an error", col=2, row=1, color="red")
    fk = d.box("FK of the answer\nlands on the ball", col=3, row=0, color="green")
    d.arrow(a, b)
    d.arrow(b, yes, label="yes")
    d.arrow(b, no, label="no")
    d.arrow(yes, fk)
    d.save(OUT / "diagram-decision.excalidraw")


if __name__ == "__main__":
    triangle()
    decision()
