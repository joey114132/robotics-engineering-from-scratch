# 레슨 15/04 도해: 테스트 세 종류가 잡는 것과 fake clock 이 시간을 테스트 손에 넘기는 구조를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def kinds():
    d = Diagram(cell=(330, 170))
    d.title("Three tests, three kinds of bug")
    u = d.box("Unit test\nfake clock + mock joint", 0, 0, "purple", w=290)
    r = d.box("Replay test\nrecorded trace", 0, 1, "purple", w=290)
    p = d.box("Property test\nrandom inputs", 0, 2, "purple", w=290)
    a = d.box("Timing and limit logic\nstale gap, direction", 1, 0, "red", w=290)
    b = d.box("Any change in output\nsign flip, new gain", 1, 1, "red", w=290)
    c = d.box("Inputs nobody imagined\nNaN, huge values", 1, 2, "red", w=290)
    for s, t in ((u, a), (r, b), (p, c)):
        d.arrow(s, t)
    d.save(OUT / "diagram-test-kinds.excalidraw")


def clock():
    d = Diagram(cell=(300, 170))
    d.title("The test owns the clock")
    real = d.box("Real clock\nproduction", 0, 0, "gray", w=210)
    fake = d.box("FakeClock\ntest advances it", 0, 1, "green", w=210)
    ctrl = d.box("Controller\nreads now()", 1, 0.5, "purple", w=210)
    joint = d.box("MockJoint\nrefuses bad torque", 2, 0.5, "yellow", w=230)
    test = d.box("Test\nasserts outputs", 2, 1.6, "blue", w=210)
    d.arrow(real, ctrl, dashed=True, label="in production")
    d.arrow(fake, ctrl, label="in tests")
    d.arrow(ctrl, joint, label="torque")
    d.arrow(test, fake, label="advance(dt)")
    d.save(OUT / "diagram-fake-clock.excalidraw")


if __name__ == "__main__":
    kinds()
    clock()
