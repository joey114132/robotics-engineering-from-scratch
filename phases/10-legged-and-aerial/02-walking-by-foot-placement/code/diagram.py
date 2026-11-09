# 레슨 10/02 도해: deadbeat 발 위치를 고르는 한 걸음의 흐름과 걸음 길이에 따른 세 가지 결과를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("One step of foot placement")
    a = d.box("End of stance:\nread x and v", 0, 0.5, "blue")
    b = d.box("Pick the next foot\nso v ends at target", 1, 0.5, "purple", w=250)
    c = d.box("Swing foot lands,\nstance flips", 2, 0.5, "yellow")
    e = d.box("Body rolls over\nthe new foot", 3, 0.5, "green")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, label="next step", route="below")
    d.save(OUT / "diagram-foot-placement-loop.excalidraw")


def lengths():
    d = Diagram(cell=(330, 170))
    d.title("What the step length does to speed")
    m = d.box("Step length\nvs the right one", 0, 1, "gray", w=240)
    s = d.box("Too short", 1, 0, "red", w=220)
    r = d.box("Right", 1, 1, "green", w=220)
    l = d.box("Too long", 1, 2, "yellow", w=220)
    rs = d.box("Speed grows every\nstep: runs away", 2, 0, "red", w=260)
    rr = d.box("Speed locks on\nthe target", 2, 1, "green", w=260)
    rl = d.box("Speed swings and\nthe body reverses", 2, 2, "yellow", w=260)
    for p, q in ((m, s), (m, r), (m, l), (s, rs), (r, rr), (l, rl)):
        d.arrow(p, q)
    d.save(OUT / "diagram-step-length-outcomes.excalidraw")


if __name__ == "__main__":
    loop()
    lengths()
