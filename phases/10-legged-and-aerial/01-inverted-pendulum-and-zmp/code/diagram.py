# 레슨 10/01 도해: LIPM 에서 시상수가 나오는 흐름과 capture point 로 발걸음을 정하는 판단을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def model():
    d = Diagram()
    d.title("From a leg to one number, Tc")
    a = d.box("Body mass at\nheight h", 0, 0, "blue")
    b = d.box("Foot pushes at p\nno leg mass", 0, 1, "yellow")
    c = d.box("x'' = (g/h)(x - p)", 1, 0.5, "purple", w=250)
    e = d.box("Solution:\ncosh and sinh", 2, 0.5, "purple")
    f = d.box("Tc = sqrt(h/g)\nfall speed", 3, 0.5, "green")
    for s, t in ((a, c), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.note("Taller body = bigger Tc = slower fall, more time to react.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-lipm-flow.excalidraw")


def capture():
    d = Diagram(cell=(330, 170))
    d.title("Where must the foot go?")
    s = d.box("Measure x and v\nxi = x + v*Tc", 0, 0.5, "blue", w=250)
    q = d.box("Is xi inside\nthe foot?", 1, 0.5, "gray", shape="diamond", w=250, h=120)
    y = d.box("Yes: ankle torque\nmoves the ZMP", 2, 0, "green", w=250)
    n = d.box("No: ankle is\nsaturated", 2, 1, "red", w=250)
    st = d.box("Step onto xi:\nbody stops there", 3, 1, "green", w=230)
    d.arrow(s, q)
    d.arrow(q, y, label="yes")
    d.arrow(q, n, label="no")
    d.arrow(n, st)
    d.save(OUT / "diagram-capture-decision.excalidraw")


if __name__ == "__main__":
    model()
    capture()
