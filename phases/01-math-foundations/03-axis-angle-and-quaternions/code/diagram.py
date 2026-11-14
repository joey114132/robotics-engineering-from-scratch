# 레슨 01/03 도해: 같은 자세를 가리키는 q 와 -q, 그리고 부호를 확인하고 뒤집는 slerp 의 판단 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def cover():
    d = Diagram()
    d.title("Two quaternions, one wrist pose")
    a = d.box("Turn 0.1 rad\nquaternion q", 0, 0, "blue")
    r = d.box("Same pose\nsame matrix R", 1, 0, "green")
    b = d.box("Turn 0.1 plus\na full turn: -q", 2, 0, "blue")
    d.arrow(a, r)
    d.arrow(b, r)
    d.save(OUT / "diagram-double-cover.excalidraw")


def flow():
    d = Diagram(numbered=True)
    d.title("Slerp with the sign fix")
    t = d.box("Target q1 arrives\nsign unknown", 0, 0, "blue")
    c = d.box("dot(q0, q1)\nnegative?", 1, 0, "yellow", shape="diamond")
    n = d.box("Flip the sign\nof q1", 2, 0, "purple")
    s = d.box("Slerp turns the\nshort way", 2, 1, "green")
    d.arrow(t, c)
    d.arrow(c, n, label="yes")
    d.arrow(c, s, label="no")
    d.arrow(n, s)
    d.note("Skip the check and the wrist turns the long way.", near=t, side="b")
    d.save(OUT / "diagram-slerp-sign-fix.excalidraw")


if __name__ == "__main__":
    cover()
    flow()
