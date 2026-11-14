# 레슨 10/02 도해: deadbeat 발 위치를 고르는 한 걸음의 흐름과 걸음 길이에 따른 세 가지 결과를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(numbered=True)
    d.title("One step of foot placement")
    a = d.box("Stance ends:\nread x and v", 0, 0, "blue", step=1)
    b = d.box("Solve for the foot\nthat ends at v target", 1, 0, "purple", step=2)
    c = d.box("Swing foot lands\nat that spot", 1, 1, "yellow", step=3)
    e = d.box("Body rolls over\nthe new foot", 0, 1, "green", step=4)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, label="next step")
    d.note("Deadbeat: the speed is exact after one step.", near=b, side="t")
    d.save(OUT / "diagram-foot-placement-loop.excalidraw")
    print("warnings", d.warnings)


def lengths():
    d = Diagram()
    d.title("What the step length does to speed")
    s = d.box("Step 0.6x\n(too short)", 0, 0, "red")
    rs = d.box("Speed 3.6 m/s by\nstep 5, still rising", 1, 0, "red")
    r = d.box("Step 1.0x\n(deadbeat)", 0, 1, "green")
    rr = d.box("Speed locks on\n0.6 m/s", 1, 1, "green")
    l = d.box("Step 1.5x\n(too long)", 0, 2, "yellow")
    rl = d.box("Speed swings, then\nreverses at step 5", 1, 2, "yellow")
    for p, q in ((s, rs), (r, rr), (l, rl)):
        d.arrow(p, q)
    d.save(OUT / "diagram-step-length-outcomes.excalidraw")
    print("warnings", d.warnings)


if __name__ == "__main__":
    loop()
    lengths()
