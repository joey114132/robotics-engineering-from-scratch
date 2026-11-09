# 레슨 08/01 도해: 바퀴 속도에서 자세까지의 계산 흐름과 오차가 경로에 들어오는 두 자리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram(cell=(330, 170))
    d.title("From wheel speeds to a pose")
    a = d.box("Left and right\nwheel speed", 0, 0.5, "blue", w=230)
    b = d.box("v = r (wr + wl) / 2\nw = r (wr - wl) / b", 1, 0.5, "purple", w=280)
    c = d.box("Add v dt and w dt\nto the pose", 2, 0.5, "purple", w=250)
    e = d.box("Pose estimate\n(x, y, heading)", 3, 0.5, "green", w=230)
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.note("r = wheel radius, b = distance between the wheels", d.margin, d.margin + 60 + 2 * d.ch - 40, size=20)
    d.save(OUT / "diagram-wheels-to-pose.excalidraw")


def errors():
    d = Diagram(cell=(330, 170))
    d.title("Two small errors, two different damages")
    r = d.box("Wheel radius r\nis 1% off", 0, 0, "yellow", w=230)
    b = d.box("Track width b\nis 1% off", 0, 1, "yellow", w=230)
    x = d.box("Every distance and\nevery turn is 1% off", 1, 0, "red", w=290)
    y = d.box("Every turn is\n1% off", 1, 1, "red", w=290)
    z = d.box("Loop does not close\nat the start", 2, 0.5, "red", w=260)
    d.arrow(r, x)
    d.arrow(b, y)
    d.arrow(x, z)
    d.arrow(y, z)
    d.note("The estimate cannot see this: it uses the same wrong r and b.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=20)
    d.save(OUT / "diagram-two-errors.excalidraw")


if __name__ == "__main__":
    chain()
    errors()
