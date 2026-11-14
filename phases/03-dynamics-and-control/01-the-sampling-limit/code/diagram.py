# 레슨 03/01 도해: 홀드된 댐퍼 명령이 낡은 속도에 작용하는 흐름과 r 구간별 거동을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def stale():
    d = Diagram(numbered=True)
    d.title("One tick of a held damper")
    a = d.box("Read the joint\nspeed: v = 1", 0, 0, "blue", step=1)
    b = d.box("Compute\ntorque = -kd * v", 1, 0, "purple", step=2)
    c = d.box("Hold that torque\nfor the whole tick", 1, 1, "yellow", step=3)
    e = d.box("Joint speed has\nalready changed", 0, 1, "red", step=4)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, label="next tick")
    d.note("Big kd or light joint: the held push goes past zero.", near=c, side="b")
    d.save(OUT / "diagram-stale-command.excalidraw")


def ranges():
    d = Diagram()
    d.title("Which zone is my r in?")
    r = d.box("r = dt*kd/J\n(0.5, 1.5, 2.5)", 0, 1, "gray")
    s = d.box("r up to 1: speed\nshrinks 1, 0.5, 0.25", 1, 0, "green")
    c = d.box("r from 1 to 2: flips\n1, -0.5, 0.25", 1, 1, "yellow")
    x = d.box("r from 2 up: grows\n1, -1.5, 2.25", 1, 2, "red")
    for t in (s, c, x):
        d.arrow(r, t)
    d.save(OUT / "diagram-r-zones.excalidraw")


if __name__ == "__main__":
    stale()
    ranges()
