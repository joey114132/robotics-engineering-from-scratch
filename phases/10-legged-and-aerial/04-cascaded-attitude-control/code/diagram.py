# 레슨 10/04 도해: 단일 PD 루프와 각도-속도 캐스케이드의 구조, 돌풍이 들어오는 자리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def single():
    d = Diagram()
    d.title("One loop: PD on the angle")
    a = d.box("Angle error", 0, 0.5, "blue", w=200)
    b = d.box("kp * error\n- kd * rate", 1, 0.5, "purple", w=210)
    c = d.box("Torque", 2, 0.5, "purple", w=180)
    p = d.box("Body: I theta''\n= tau + gust", 3, 0.5, "yellow", w=230)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, p)
    d.arrow(p, a, label="angle", route="below")
    d.note("A steady gust d leaves a steady error d / kp.", d.margin, d.margin + 60 + 2 * d.ch - 30, size=22)
    d.save(OUT / "diagram-single-pd.excalidraw")


def cascade():
    d = Diagram(cell=(280, 170))
    d.title("Two loops: angle outside, rate inside")
    a = d.box("Angle error", 0, 0.5, "blue", w=190)
    b = d.box("Outer P:\nrate command", 1, 0.5, "purple", w=200)
    c = d.box("Inner PI on\nrate error", 2, 0.5, "purple", w=200)
    p = d.box("Body: I theta''\n= tau + gust", 3, 0.5, "yellow", w=210)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, p)
    d.arrow(p, c, label="rate (gyro)", route="below")
    d.note("The inner integral soaks up the gust. Outer gains stay as they were.", d.margin, d.margin + 60 + 2 * d.ch - 30, size=22)
    d.save(OUT / "diagram-cascade.excalidraw")


if __name__ == "__main__":
    single()
    cascade()
