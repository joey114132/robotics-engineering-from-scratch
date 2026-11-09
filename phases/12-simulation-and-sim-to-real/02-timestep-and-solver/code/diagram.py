# 레슨 12/02 도해: 두 적분기의 update 순서 차이와, step 크기를 훑어 결과를 확인하는 절차를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def order():
    d = Diagram(cell=(330, 170))
    d.title("Two ways to take one step")
    a = d.box("Explicit Euler\nx uses the OLD v", 0, 0, "red", w=270)
    a2 = d.box("v uses the old force", 1, 0, "gray", w=250)
    a3 = d.box("Energy grows\nevery step", 2, 0, "red", w=230)
    b = d.box("Semi-implicit Euler\nx uses the NEW v", 0, 1.3, "green", w=270)
    b2 = d.box("v first, then x", 1, 1.3, "gray", w=250)
    b3 = d.box("Energy wobbles\nbut stays bounded", 2, 1.3, "green", w=230)
    for s, t in ((a, a2), (a2, a3), (b, b2), (b2, b3)):
        d.arrow(s, t)
    d.save(OUT / "diagram-update-order.excalidraw")


def sweep():
    d = Diagram(cell=(300, 170))
    d.title("Never trust one step size")
    run = d.box("Run at\ndt = 1e-5", 0, 0.5, "blue", w=200)
    ref = d.box("Reference\nanswer", 1, 0.5, "green", w=200)
    swp = d.box("Sweep dt up,\ncompare each run", 2, 0.5, "yellow", w=230)
    mat = d.box("Result moves?\nStop and shrink dt", 3, 0.5, "red", w=240)
    for s, t in ((run, ref), (ref, swp), (swp, mat)):
        d.arrow(s, t)
    d.note("The step you ship must sit on the flat part of the sweep.", d.margin, d.margin + 60 + 1.5 * d.ch + 40, size=22)
    d.save(OUT / "diagram-dt-sweep.excalidraw")


if __name__ == "__main__":
    order()
    sweep()
