# 레슨 15/01 도해: 결함이 제어 루프의 어디에 들어가는지, 어떤 검사가 어떤 결함을 잡는지 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(cell=(280, 170))
    d.title("Where each fault enters the loop")
    r = d.box("Reference", 0, 1, "blue", w=190)
    c = d.box("Controller\nPD", 1, 1, "purple", w=190)
    a = d.box("Actuator", 2, 1, "gray", w=190)
    j = d.box("Joint", 3, 1, "yellow", w=190)
    s = d.box("Sensor", 3, 2, "gray", w=190)
    ws = d.box("Wrong sign", 1, 0, "red", w=190)
    sa = d.box("Saturation", 2, 0, "red", w=190)
    sf = d.box("Stuck\nDropout\nDelay", 4, 2, "red", w=190, h=110)
    d.arrow(r, c)
    d.arrow(c, a)
    d.arrow(a, j)
    d.arrow(j, s)
    d.arrow(s, c, route="below")
    d.arrow(ws, c, dashed=True)
    d.arrow(sa, a, dashed=True)
    d.arrow(sf, s, dashed=True)
    d.save(OUT / "diagram-fault-points.excalidraw")


def checks():
    d = Diagram(cell=(330, 170))
    d.title("Which cheap check sees which fault")
    f = d.box("Reading flat\nwhile torque on", 0, 0, "purple", w=250)
    j = d.box("Reading jumps\nin one tick", 0, 1, "purple", w=250)
    g = d.box("Error grows\nin 100 ms", 0, 2, "purple", w=250)
    l = d.box("Not at target\nafter 2 s", 0, 3, "purple", w=250)
    st = d.box("Stuck sensor", 1, 0, "red", w=210)
    dr = d.box("Dropout", 1, 1, "red", w=210)
    ws = d.box("Wrong sign\nDelay", 1, 2, "red", w=210)
    sa = d.box("Saturation", 1, 3, "red", w=210)
    for a, b in ((f, st), (j, dr), (g, ws), (l, sa)):
        d.arrow(a, b)
    d.note("Saturation is the quiet one: nothing trips until the clock does.", d.margin, d.margin + 60 + 4 * d.ch - 40, size=20)
    d.save(OUT / "diagram-fault-checks.excalidraw")


if __name__ == "__main__":
    loop()
    checks()
