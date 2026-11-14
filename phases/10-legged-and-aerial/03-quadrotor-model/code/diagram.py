# 레슨 10/03 도해: 추력이 기울기에 따라 위쪽과 옆쪽으로 나뉘는 방식과 토크에서 옆 이동까지의 적분 사슬을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def forces():
    d = Diagram()
    d.title("One thrust, split by the tilt")
    t = d.box("Thrust T,\ntilted by theta", 0, 0, "yellow")
    h = d.box("Sideways:\nT sin(theta)", 1, 0, "purple")
    v = d.box("Up force:\nT cos(theta) - m g", 0, 1, "green")
    ds = d.box("At T = m g and\ntheta > 0: it sinks", 1, 1, "red")
    d.arrow(t, h)
    d.arrow(t, v)
    d.arrow(v, ds)
    d.note("Level (theta = 0) and T = m g: it hovers.", near=v, side="b")
    d.save(OUT / "diagram-thrust-split.excalidraw")
    print("warnings", d.warnings)


def chain():
    d = Diagram(numbered=True)
    d.title("Why sideways motion is slow to start")
    a = d.box("Torque tau", 0, 0, "blue", step=1)
    b = d.box("Pitch rate\nomega", 1, 0, "purple", step=2)
    c = d.box("Pitch angle\ntheta", 2, 0, "purple", step=3)
    e = d.box("Sideways\nacceleration", 2, 1, "purple", step=4)
    f = d.box("Position x", 1, 1, "green", step=5)
    for p, q in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(p, q)
    d.note("x grows like t^4", near=f, side="l")
    d.save(OUT / "diagram-torque-to-position.excalidraw")
    print("warnings", d.warnings)


if __name__ == "__main__":
    forces()
    chain()
