# 레슨 04/01 도해: 전압에서 출력 토크까지의 흐름과, 감속비가 부하 관성을 N^2 로 줄이는 모양을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram(cell=(280, 170))
    d.title("From voltage to output torque")
    v = d.box("Voltage V", 0, 0, "blue", w=190)
    i = d.box("Current\n(V - kt*w) / R", 1, 0, "purple", w=220)
    t = d.box("Motor torque\nkt * current", 2, 0, "purple", w=210)
    g = d.box("Gearbox\ntorque x N", 3, 0, "yellow", w=190)
    o = d.box("Output torque\nspeed / N", 4, 0, "green", w=210)
    e = d.box("Back-EMF\nkt * w", 1.5, 1, "red", w=210)
    for a, b in ((v, i), (i, t), (t, g), (g, o)):
        d.arrow(a, b)
    d.arrow(t, e)
    d.arrow(e, i)
    d.note("The faster the motor spins, the less current it gets: that is the torque-speed line.", d.margin, d.margin + 60 + 2 * d.ch - 40, size=20)
    d.save(OUT / "diagram-motor-chain.excalidraw")


def inertia():
    d = Diagram(cell=(320, 170))
    d.title("A big ratio hides the load")
    jl = d.box("Load inertia\nJ_L (output side)", 0, 0, "yellow", w=240)
    div = d.box("Divide by N^2", 1, 0, "purple", w=220)
    seen = d.box("Seen by motor\nJ_L / N^2", 2, 0, "blue", w=230)
    jr = d.box("Rotor inertia\nJ_r", 1, 1, "blue", w=230)
    res = d.box("N = 100: load shrinks\n10,000 times", 2, 1, "red", w=240)
    d.arrow(jl, div)
    d.arrow(div, seen)
    d.arrow(seen, res)
    d.arrow(jr, res, label="dominates")
    d.note("The drive sees almost the same inertia with or without the load.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=20)
    d.save(OUT / "diagram-reflected-inertia.excalidraw")


if __name__ == "__main__":
    chain()
    inertia()
