# 레슨 00/03 도해: 같은 사분의 일 바퀴를 두 단위로 읽는 법과, 큰 각도를 한 바퀴 안으로 감는 순서
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def names():
    d = Diagram()
    d.title("One turn, two names")
    t = d.box("A quarter turn", col=0, row=0.5, color="yellow")
    g = d.box("90 degrees\n360 = full turn", col=1, row=0, color="blue")
    r = d.box("1.57 radians\n6.28 = full turn", col=1, row=1, color="purple")
    c = d.box("Code uses\nradians", col=2, row=1, color="green")
    d.arrow(t, g)
    d.arrow(t, r)
    d.arrow(r, c)
    d.note("convert degrees before calling cos or sin", near=c, side="b")
    d.save(OUT / "diagram-two-names.excalidraw")


def wrap():
    d = Diagram()
    d.title("Wrapping a big angle")
    a = d.box("Angle\n450 degrees", col=0, row=0, color="red")
    s = d.box("Take away\nfull turns", col=1, row=0, color="purple")
    w = d.box("Angle\n90 degrees", col=2, row=0, color="green")
    d.arrow(a, s)
    d.arrow(s, w, label="same direction")
    d.note("450 and 90 point the same way", near=w, side="b")
    d.save(OUT / "diagram-wrap-angle.excalidraw")


if __name__ == "__main__":
    names()
    wrap()
