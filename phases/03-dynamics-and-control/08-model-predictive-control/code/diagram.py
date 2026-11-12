# 레슨 03/08 도해: 매 tick 계획하고 첫 입력만 쓰는 후퇴 horizon 루프와, 한계를 자르는 쪽과 아는 쪽의 차이를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("Plan far, commit one step, plan again")
    a = d.box("Measure\nstate x", 0, 0.5, "yellow")
    b = d.box("Plan N steps\nwithin |u| <= umax", 1, 0.5, "purple", w=250)
    c = d.box("Apply only\nthe first u", 2, 0.5, "green")
    e = d.box("Plant moves\none tick", 3, 0.5, "yellow")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, label="next tick", route="below")
    d.note("The rest of the plan is thrown away. A fresh plan replaces it.", d.margin, d.margin + 60 + 2.2 * d.ch, size=22)
    d.save(OUT / "diagram-mpc-loop.excalidraw")


def clip_vs_know():
    d = Diagram(cell=(330, 170))
    d.title("Clipping hides the limit. MPC plans with it.")
    s = d.box("Torque limit\nexists", 0, 1, "gray", w=220)
    c = d.box("Clip an LQR gain\nthe gain never saw the limit", 1, 0, "red", w=280)
    p = d.box("MPC\nthe limit is a constraint", 1, 2, "blue", w=280)
    co = d.box("Overshoots,\nbrakes too late", 2, 0, "red", w=220)
    po = d.box("Starts braking\nin time", 2, 2, "green", w=220)
    for x, y in ((s, c), (s, p), (c, co), (p, po)):
        d.arrow(x, y)
    d.save(OUT / "diagram-mpc-clip.excalidraw")


if __name__ == "__main__":
    loop()
    clip_vs_know()
