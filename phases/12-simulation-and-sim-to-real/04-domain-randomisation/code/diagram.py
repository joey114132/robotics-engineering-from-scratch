# 레슨 12/04 도해: 무작위 plant 로 controller 를 평가하는 흐름과, 범위가 좁을 때 맞을 때 넓을 때의 결과를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(cell=(300, 170))
    d.title("Evaluate a fixed controller on many plants")
    rng = d.box("Pick a width w:\nscale each parameter\nby 1 +- w", 0, 0.5, "blue", w=240, h=110)
    plants = d.box("N random plants", 1, 0.5, "yellow", w=210)
    ctrl = d.box("Same fixed PD\ncontroller on each", 2, 0.5, "purple", w=230)
    rate = d.box("Success rate\nand mean cost", 3, 0.5, "green", w=220)
    for s, t in ((rng, plants), (plants, ctrl), (ctrl, rate)):
        d.arrow(s, t)
    d.arrow(rate, rng, route="below", label="change w or the gains, repeat")
    d.save(OUT / "diagram-dr-loop.excalidraw")


def widths():
    d = Diagram(cell=(330, 170))
    d.title("How wide should the range be?")
    nar = d.box("Range narrower than\nthe real plant", 0, 0, "red", w=290)
    rn = d.box("Fast on paper,\nfails on the real one", 1, 0, "red", w=280)
    mat = d.box("Range matches\nthe real plant", 0, 1.1, "green", w=290)
    rm = d.box("Reliable and fast", 1, 1.1, "green", w=280)
    wid = d.box("Range far wider than\nthe real plant", 0, 2.2, "yellow", w=290)
    rw = d.box("Reliable but slower:\nit guards against plants\nthat never occur", 1, 2.2, "yellow", w=290, h=110)
    for s, t in ((nar, rn), (mat, rm), (wid, rw)):
        d.arrow(s, t)
    d.save(OUT / "diagram-dr-widths.excalidraw")


if __name__ == "__main__":
    loop()
    widths()
