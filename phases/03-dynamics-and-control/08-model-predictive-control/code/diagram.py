# 레슨 03/08 도해: 매 tick 계획하고 첫 입력만 쓰는 후퇴 horizon 루프와, 한계를 자르는 쪽과 아는 쪽의 차이를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(numbered=True)
    d.title("Plan far, commit one step, plan again")
    a = d.box("Measure the car:\nposition and speed", 0, 0, "yellow", step=1)
    b = d.box("Plan N steps\nwithin |u| <= umax", 1, 0, "purple", step=2)
    c = d.box("Apply only the\nfirst push u", 1, 1, "green", step=3)
    e = d.box("Car moves\none tick", 0, 1, "yellow", step=4)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, label="next tick")
    d.note("The rest of the plan is thrown away.", near=c, side="b")
    d.save(OUT / "diagram-mpc-loop.excalidraw")


def clip_vs_know():
    d = Diagram()
    d.title("Clipping hides the limit. MPC plans with it.")
    s = d.box("Push limit\nexists", 0.5, 0, "gray")
    c = d.box("Clip an LQR gain:\nit never saw the limit", 0, 1, "red")
    p = d.box("MPC: the limit\nis a constraint", 1, 1, "blue")
    co = d.box("Overshoots,\nbrakes too late", 0, 2, "red")
    po = d.box("Starts braking\nin time", 1, 2, "green")
    for x, y in ((s, c), (s, p), (c, co), (p, po)):
        d.arrow(x, y)
    d.save(OUT / "diagram-mpc-clip.excalidraw")


if __name__ == "__main__":
    loop()
    clip_vs_know()
