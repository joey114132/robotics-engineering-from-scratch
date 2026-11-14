# 레슨 15/04 도해: 테스트 세 종류가 잡는 것과 fake clock 이 시간을 테스트 손에 넘기는 구조를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def kinds():
    d = Diagram()
    d.title("Three tests, three kinds of bug")
    rows = (("Unit test\nstep 0.3 s, is the arm closer?", "Wrong direction\nor a late update"),
            ("Replay test\nsame inputs, same torque?", "Any change in output\nsign flip, new gain"),
            ("Property test\nthousands of random inputs", "Inputs nobody imagined\nNaN, huge values"))
    for i, (test, bug) in enumerate(rows):
        a = d.box(test, col=0, row=i, color="purple")
        b = d.box(bug, col=1, row=i, color="red")
        d.arrow(a, b, label="catches")
    d.save(OUT / "diagram-test-kinds.excalidraw")
    return d


def clock():
    d = Diagram()
    d.title("The test owns the clock")
    test = d.box("Test\nadvances the clock", col=0, row=0, color="blue")
    fake = d.box("FakeClock\nmoves only on advance(dt)", col=0, row=1, color="green")
    real = d.box("Real clock\nonly in production", col=1, row=2, color="gray")
    ctrl = d.box("Controller\nasks the clock for now()", col=0, row=2, color="purple")
    joint = d.box("MockJoint\nrefuses bad torque", col=0, row=3, color="yellow")
    d.arrow(test, fake, label="advance")
    d.arrow(fake, ctrl, label="now()")
    d.arrow(real, ctrl, dashed=True, label="now()")
    d.arrow(ctrl, joint, label="torque")
    d.save(OUT / "diagram-fake-clock.excalidraw")
    return d


if __name__ == "__main__":
    for dd in (kinds(), clock()):
        print(dd.warnings)
