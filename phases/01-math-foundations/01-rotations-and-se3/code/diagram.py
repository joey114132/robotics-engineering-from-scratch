# 레슨 01/01 도해: 카메라에서 베이스로 가는 transform 흐름과 드론 코가 회전 순서에 따라 다른 곳을 향하는 두 길을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram(numbered=True)
    d.title("Camera numbers to base numbers")
    a = d.box("Cup seen by camera\np_cam", 0, 0, "blue")
    t = d.box("T_base_cam\nturn, then shift", 1, 0, "purple")
    b = d.box("Cup seen by base\nR p_cam + p", 2, 0, "green")
    d.arrow(a, t)
    d.arrow(t, b)
    d.arrow(b, a, label="inverse goes back", route="below")
    d.save(OUT / "diagram-transform-chain.excalidraw")


def order():
    d = Diagram()
    d.title("Same two turns, two orders, two answers")
    for row, (turns, nose, color) in enumerate((("Roll x,\nthen spin z", "Nose left\n(0, 1, 0)", "green"),
                                                ("Spin z,\nthen roll x", "Nose up\n(0, 0, 1)", "red"))):
        s = d.box("Nose at door\n(1, 0, 0)", 0, row, "blue")
        t = d.box(turns, 1, row, "purple")
        r = d.box(nose, 2, row, color)
        d.arrow(s, t)
        d.arrow(t, r)
    d.save(OUT / "diagram-rotation-order.excalidraw")


if __name__ == "__main__":
    chain()
    order()
