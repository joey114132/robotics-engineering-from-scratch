# 레슨 09/01 도해: 프로파일 세 가지가 가속도에 미치는 영향, 가속도 계단이 관절에 닿는 경로를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def choice():
    d = Diagram()
    d.title("One arm move, three profiles")
    c = d.box("Cubic:\n4 conditions", 0, 0, "blue")
    q = d.box("Quintic:\n6 conditions", 0, 1, "blue")
    t = d.box("Trapezoid:\nflat cruise", 0, 2, "blue")
    rc = d.box("Acceleration\njumps at the ends", 1, 0, "red")
    rq = d.box("Acceleration\nstarts and ends at 0", 1, 1, "green")
    rt = d.box("Acceleration\nsteps four times", 1, 2, "red")
    for a, b in ((c, rc), (q, rq), (t, rt)):
        d.arrow(a, b)
    d.save(OUT / "diagram-profile-choice.excalidraw")


def jerk_chain():
    d = Diagram()
    d.title("From a step in acceleration to a rattle")
    a = d.box("Cubic acceleration\nsteps 0 to 1.5 rad/s²", 0, 0, "red")
    b = d.box("Jerk spike:\n1.5 / 0.002 = 750", 0, 1, "red")
    c = d.box("Motor torque\nsteps at once", 0, 2, "yellow")
    e = d.box("Arm knocks,\ngearbox rattles", 0, 3, "red")
    f = d.box("Quintic starts\nat acceleration 0", 1, 0, "green")
    g = d.box("Peak jerk\nonly 7.5", 1, 1, "green")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(f, g)
    d.save(OUT / "diagram-jerk-chain.excalidraw")


if __name__ == "__main__":
    choice()
    jerk_chain()
