# 레슨 09/01 도해: 프로파일 세 가지의 경계 조건과 결과, 가속도 계단이 관절에 닿는 경로를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def choice():
    d = Diagram(cell=(330, 170))
    d.title("Three ways to move from q0 to qf in time T")
    s = d.box("Same move\nq0 to qf in T", 0, 1, "gray", w=240)
    c = d.box("Cubic\n4 conditions", 1, 0, "blue", w=240)
    q = d.box("Quintic\n6 conditions", 1, 1, "blue", w=240)
    t = d.box("Trapezoid\nflat cruise", 1, 2, "blue", w=240)
    rc = d.box("Acceleration\njumps at ends", 2, 0, "red", w=240)
    rq = d.box("Acceleration\nstarts at zero", 2, 1, "green", w=240)
    rt = d.box("Acceleration\nsteps 4 times", 2, 2, "red", w=240)
    for a, b in ((s, c), (s, q), (s, t), (c, rc), (q, rq), (t, rt)):
        d.arrow(a, b)
    d.save(OUT / "diagram-profile-choice.excalidraw")


def jerk_chain():
    d = Diagram()
    d.title("How an acceleration step reaches the joint")
    a = d.box("Acceleration\nsteps 0 to a", 0, 0, "red")
    b = d.box("Jerk spike\n= step / dt", 1, 0, "red")
    c = d.box("Motor torque\nsteps at once", 2, 0, "yellow")
    e = d.box("Joint jerks,\ngearbox rattles", 3, 0, "red")
    f = d.box("Quintic: start\nat acceleration 0", 1, 1, "green")
    g = d.box("Jerk stays\nfinite", 2, 1, "green")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(f, g)
    d.note("Finer sampling makes the spike taller, not shorter.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-jerk-chain.excalidraw")


if __name__ == "__main__":
    choice()
    jerk_chain()
