# 레슨 12/04 도해: 무작위 plant 로 controller 를 평가하는 흐름과, 범위가 좁을 때 맞을 때 넓을 때의 결과를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(numbered=True)
    d.title("Test one fixed controller on many arms")
    rng = d.box("Pick a\nwidth w", 0, 0, "blue")
    plants = d.box("N different\narms", 1, 0, "yellow")
    ctrl = d.box("Same fixed\nPD gains", 2, 0, "purple")
    rate = d.box("Success rate,\nmean cost", 2, 1, "green")
    for s, t in ((rng, plants), (plants, ctrl), (ctrl, rate)):
        d.arrow(s, t)
    d.arrow(rate, rng, label="change w or gains, repeat")
    d.note("every parameter\ntimes (1 +- w)", near=rng, side="t")
    d.save(OUT / "diagram-dr-loop.excalidraw")


def widths():
    d = Diagram()
    d.title("How wide should the range be?")
    nar = d.box("Range narrower\nthan the real arm", 0, 0, "red")
    rn = d.box("Fast on paper,\nfails on the real arm", 1, 0, "red")
    mat = d.box("Range matches\nthe real arm", 0, 1, "green")
    rm = d.box("Reliable and fast", 1, 1, "green")
    wid = d.box("Range far wider\nthan the real arm", 0, 2, "yellow")
    rw = d.box("Reliable but slower:\nguards against arms\nthat never occur", 1, 2, "yellow")
    for s, t in ((nar, rn), (mat, rm), (wid, rw)):
        d.arrow(s, t)
    d.save(OUT / "diagram-dr-widths.excalidraw")


if __name__ == "__main__":
    loop()
    widths()
