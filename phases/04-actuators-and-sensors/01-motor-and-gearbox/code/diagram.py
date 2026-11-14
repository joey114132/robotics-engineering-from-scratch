# 레슨 04/01 도해: 모터 안에서 전압이 전류와 토크가 되고 속도가 back-EMF 로 되밀어 내는 고리, 기어박스가 flywheel 관성을 N^2 로 줄이는 모양을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram()
    d.title("A spinning motor fights its own supply")
    v = d.box("Supply voltage V", col=0, row=0, color="blue")
    i = d.box("Current\n(V - kt*w)/R", col=1, row=0, color="purple")
    t = d.box("Torque\nkt * current", col=2, row=0, color="purple")
    w = d.box("Motor speeds up\nspeed w grows", col=2, row=1, color="yellow")
    e = d.box("Back-EMF\nkt * w", col=1, row=1, color="red")
    d.arrow(v, i)
    d.arrow(i, t)
    d.arrow(t, w)
    d.arrow(w, e)
    d.arrow(e, i, label="subtracts")
    d.note("Faster spin, less current, less torque.", near=e, side="b")
    d.save(OUT / "diagram-motor-chain.excalidraw")


def inertia():
    d = Diagram()
    d.title("A big ratio hides the flywheel")
    jl = d.box("Flywheel inertia\nJ_L = 2e-3", col=0, row=0, color="yellow")
    div = d.box("Gearbox divides\nby N squared", col=1, row=0, color="purple")
    seen = d.box("Motor feels\nJ_L / N^2", col=2, row=0, color="blue")
    jr = d.box("Rotor inertia\nJ_r = 2e-5", col=2, row=1, color="blue")
    res = d.box("N = 100: flywheel\ncounts 1% of rotor", col=1, row=1, color="green")
    d.arrow(jl, div)
    d.arrow(div, seen)
    d.arrow(seen, res)
    d.arrow(jr, res)
    d.note("At N = 100 the drive barely notices the flywheel.", near=res, side="b")
    d.save(OUT / "diagram-reflected-inertia.excalidraw")


if __name__ == "__main__":
    chain()
    inertia()
