# 레슨 03/01 도해: 홀드된 댐퍼 명령이 낡은 속도에 작용하는 흐름과 r 구간별 거동을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def stale():
    d = Diagram()
    d.title("Why a held damper can push the wrong way")
    a = d.box("Tick starts:\nread v", 0, 0, "blue")
    b = d.box("Compute\ntorque = -kd * v", 1, 0, "purple")
    c = d.box("Hold torque\nfor the whole dt", 2, 0, "yellow")
    e = d.box("v has already\nchanged", 3, 0, "red")
    f = d.box("Next tick pushes\nagainst old v", 3, 1, "red")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.note("Big kd or small J: the held push overshoots zero.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-stale-command.excalidraw")


def ranges():
    d = Diagram(cell=(300, 150))
    d.title("Four zones of r = dt*kd/J")
    r = d.box("Compute\nr = dt*kd/J", 0, 1.5, "gray", w=200)
    s = d.box("r <= 1\nsmooth (r=1: zero in 1 tick)", 1, 0, "green", w=300)
    c = d.box("1 < r < 2\nchatter: flips, decays", 1, 1, "yellow", w=300)
    x = d.box("r >= 2\nnever decays: BLOCK", 1, 2, "red", w=300)
    for t in (s, c, x):
        d.arrow(r, t)
    d.save(OUT / "diagram-r-zones.excalidraw")


if __name__ == "__main__":
    stale()
    ranges()
