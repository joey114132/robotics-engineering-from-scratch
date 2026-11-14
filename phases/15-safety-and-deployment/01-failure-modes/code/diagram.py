# 레슨 15/01 도해: 결함이 제어 루프의 어디에 들어가는지, 어떤 검사가 어떤 결함을 잡는지 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("Where each fault enters the loop")
    t = d.box("Target\n1 rad", col=0, row=0, color="blue")
    c = d.box("Controller\npushes like a spring", col=1, row=0, color="purple")
    m = d.box("Motor\nturns the joint", col=2, row=0, color="gray")
    j = d.box("Joint\nthe arm itself", col=2, row=1, color="yellow")
    s = d.box("Sensor\nreports the angle", col=1, row=1, color="gray")
    ws = d.box("Wrong sign\npush is flipped", col=1, row=-1, color="red")
    sa = d.box("Saturation\npush is capped low", col=2, row=-1, color="red")
    sf = d.box("Bad reading\nstuck, dropout, delay", col=0, row=1, color="red")
    d.arrow(t, c)
    d.arrow(c, m)
    d.arrow(m, j)
    d.arrow(j, s)
    d.arrow(s, c)
    d.arrow(ws, c, dashed=True)
    d.arrow(sa, m, dashed=True)
    d.arrow(sf, s, dashed=True)
    d.save(OUT / "diagram-fault-points.excalidraw")
    return d


def checks():
    d = Diagram()
    d.title("Which cheap check sees which fault")
    rows = (("Reading flat\nwhile torque is on", "Stuck sensor"),
            ("Reading jumps\nin one tick", "Dropout"),
            ("Error grows\nin 100 ms", "Wrong sign, delay"),
            ("Not at target\nafter 2 s", "Saturation"))
    for i, (check, fault) in enumerate(rows):
        a = d.box(check, col=0, row=i, color="purple")
        b = d.box(fault, col=1, row=i, color="red")
        d.arrow(a, b, label="catches")
        if fault == "Saturation":
            d.note("The quiet one: only the clock catches it", near=b, side="b")
    d.save(OUT / "diagram-fault-checks.excalidraw")
    return d


if __name__ == "__main__":
    for dd in (loop(), checks()):
        print(dd.warnings)
