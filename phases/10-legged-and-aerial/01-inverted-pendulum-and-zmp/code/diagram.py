# 레슨 10/01 도해: 몸 하나와 다리 하나에서 시상수 Tc 가 나오는 흐름과 capture point 로 발걸음을 정하는 판단을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def model():
    d = Diagram()
    d.title("From a leg to one number, Tc")
    a = d.box("Body: one mass\nat height h", 0, 0, "blue")
    b = d.box("Foot at p,\nleg has no mass", 0, 1, "yellow")
    c = d.box("Gravity pulls it on:\nx'' = (g/h)(x - p)", 1, 0.5, "purple")
    e = d.box("Fall speed Tc =\nsqrt(h/g) = 0.30 s", 2, 0.5, "green")
    d.arrow(a, c)
    d.arrow(b, c)
    d.arrow(c, e, label="solve it")
    d.note("Taller body, bigger Tc, slower fall.", near=e, side="b")
    d.save(OUT / "diagram-lipm-flow.excalidraw")
    print("warnings", d.warnings)


def capture():
    d = Diagram()
    d.title("Where must the foot go?")
    s = d.box("Measure x, v:\nxi = x + v*Tc", 0, 0, "blue")
    q = d.box("Is xi inside\nthe foot?", 1, 0, "gray")
    n = d.box("No: step onto xi,\nbody stops there", 2, 0, "red")
    y = d.box("Yes: ankle moves\nthe ZMP", 1, 1, "green")
    d.arrow(s, q)
    d.arrow(q, n, label="no")
    d.arrow(q, y, label="yes")
    d.note("Shove 0.4 m/s: xi = 0.12 m, foot reaches 0.05 m", near=s, side="b")
    d.save(OUT / "diagram-capture-decision.excalidraw")
    print("warnings", d.warnings)


if __name__ == "__main__":
    model()
    capture()
