# 레슨 10/04 도해: 단일 PD 루프와 각도-속도 캐스케이드의 구조, 돌풍이 들어오는 자리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def single():
    d = Diagram()
    d.title("One loop: PD on the angle")
    a = d.box("Angle error\n(how far tilted)", 0, 0, "blue")
    b = d.box("PD pushes back:\nkp * error - kd * rate", 1, 0, "purple")
    p = d.box("Drone: I theta''\n= tau + gust", 1, 1, "yellow")
    d.arrow(a, b)
    d.arrow(b, p, label="torque tau")
    d.arrow(p, a, label="angle")
    d.note("A steady gust d leaves an error d / kp = 6.4 deg.", near=p, side="b")
    d.save(OUT / "diagram-single-pd.excalidraw")
    print("warnings", d.warnings)


def cascade():
    d = Diagram()
    d.title("Two loops: angle outside, rate inside")
    a = d.box("Angle error", 0, 0, "blue")
    b = d.box("Outer P:\nrate command", 1, 0, "purple")
    c = d.box("Inner PI on\nrate error", 1, 1, "purple")
    p = d.box("Drone: I theta''\n= tau + gust", 0, 1, "yellow")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, p, label="torque")
    d.arrow(p, a, label="angle")
    d.arrow(p, c, label="turn rate")
    d.save(OUT / "diagram-cascade.excalidraw")
    print("warnings", d.warnings)


if __name__ == "__main__":
    single()
    cascade()
