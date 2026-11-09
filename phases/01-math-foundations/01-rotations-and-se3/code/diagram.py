# 레슨 01/01 도해: 카메라에서 베이스로 가는 transform 흐름과 회전 순서에 따른 결과 차이를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram()
    d.title("Cup in camera frame to cup in base frame")
    a = d.box("Cup in camera\np_cam", 0, 0, "blue")
    t = d.box("T_base_cam\nR and p", 1, 0, "purple")
    b = d.box("Cup in base\np_base = R p_cam + p", 2, 0, "green", w=260)
    inv = d.box("Inverse\nR^T and -R^T p", 2, 1, "gray", w=260)
    d.arrow(a, t)
    d.arrow(t, b)
    d.arrow(b, inv, label="invert", label_dx=45)
    d.note("One matrix goes one way. Its inverse goes the other.", d.margin, d.margin + 60 + 2 * d.ch - 30, size=20)
    d.save(OUT / "diagram-transform-chain.excalidraw")


def order():
    d = Diagram(cell=(330, 170))
    d.title("Same two turns, two orders, two answers")
    p = d.box("Point (1, 0, 0)", 0, 0.5, "blue", w=220)
    a = d.box("Turn 90 deg about x,\nthen 90 deg about z", 1, 0, "purple", w=260)
    b = d.box("Turn 90 deg about z,\nthen 90 deg about x", 1, 1, "purple", w=260)
    ra = d.box("(0, 1, 0)", 2, 0, "green", w=200)
    rb = d.box("(0, 0, 1)", 2, 1, "red", w=200)
    for s, t in ((p, a), (p, b), (a, ra), (b, rb)):
        d.arrow(s, t)
    d.save(OUT / "diagram-rotation-order.excalidraw")


if __name__ == "__main__":
    chain()
    order()
