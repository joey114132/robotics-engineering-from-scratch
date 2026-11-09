# 레슨 10/03 도해: 추력 벡터가 수직과 수평으로 나뉘는 방식과 토크에서 옆 이동까지의 적분 사슬을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def forces():
    d = Diagram()
    d.title("One thrust, split by the tilt")
    t = d.box("Thrust T along\nthe body axis", 0, 0.5, "blue")
    th = d.box("Pitch theta tilts\nthe axis", 0, 1.5, "yellow")
    v = d.box("Up: T cos(theta) - m g", 1, 0, "green", w=250)
    h = d.box("Sideways:\nT sin(theta)", 1, 1, "purple", w=250)
    hv = d.box("Hover: T = m g\nwhen theta = 0", 2, 0, "green", w=230)
    ds = d.box("Tilt at T = m g:\nit sinks", 2, 1, "red", w=230)
    for a, b in ((t, v), (t, h), (th, h), (v, hv), (h, ds)):
        d.arrow(a, b)
    d.save(OUT / "diagram-thrust-split.excalidraw")


def chain():
    d = Diagram(cell=(260, 170))
    d.title("Why sideways motion is slow to start")
    a = d.box("Torque tau", 0, 0.5, "blue", w=190)
    b = d.box("Pitch rate\nomega", 1, 0.5, "purple", w=190)
    c = d.box("Pitch angle\ntheta", 2, 0.5, "purple", w=190)
    e = d.box("Sideways\nacceleration", 3, 0.5, "purple", w=190)
    f = d.box("Position x", 4, 0.5, "green", w=190)
    for p, q in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(p, q)
    d.note("Four integrations from torque to position: x grows like t^4.", d.margin, d.margin + 60 + 2 * d.ch - 40, size=22)
    d.save(OUT / "diagram-torque-to-position.excalidraw")


if __name__ == "__main__":
    forces()
    chain()
