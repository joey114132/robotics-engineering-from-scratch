# 레슨 12/02 도해: 두 적분기의 update 순서 차이와, step 크기를 훑어 결과를 확인하는 절차를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def order():
    d = Diagram()
    d.title("Two ways to take one step")
    a = d.box("Explicit Euler:\nmove x with the OLD speed", 0, 0, "red")
    a2 = d.box("Crate gains energy\nevery step", 1, 0, "red")
    b = d.box("Semi-implicit Euler:\nspeed first, then move x", 0, 1, "green")
    b2 = d.box("Crate energy wobbles\nbut stays bounded", 1, 1, "green")
    d.arrow(a, a2)
    d.arrow(b, b2)
    d.save(OUT / "diagram-update-order.excalidraw")


def sweep():
    d = Diagram(numbered=True)
    d.title("Never trust one step size")
    run = d.box("Drop the crate\nat a tiny dt", 0, 0, "blue")
    ref = d.box("Keep that bounce\nas the reference", 1, 0, "green")
    swp = d.box("Raise dt, rerun,\ncompare to the reference", 2, 0, "yellow")
    bad = d.box("Answer moves?\nShrink dt again", 2, 1, "red")
    for s, t in ((run, ref), (ref, swp), (swp, bad)):
        d.arrow(s, t)
    d.note("Ship a dt from the flat part of the sweep.", near=bad, side="l")
    d.save(OUT / "diagram-dt-sweep.excalidraw")


if __name__ == "__main__":
    order()
    sweep()
