# 레슨 08/01 도해: 바퀴 속도에서 자세까지의 계산 흐름과 오차가 경로에 들어오는 두 자리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram(numbered=True)
    d.title("From wheel speeds to a pose")
    a = d.box("Left and right\nwheel speed", 0, 0, "blue")
    b = d.box("v = r (wr + wl) / 2\nw = r (wr - wl) / b", 1, 0, "purple")
    c = d.box("Add v dt and w dt\nto the pose", 2, 0, "purple")
    e = d.box("Pose estimate\n(x, y, heading)", 3, 0, "green")
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.note("10 and 14 rad/s give v = 0.6, w = 0.67", near=b, side="b")
    d.save(OUT / "diagram-wheels-to-pose.excalidraw")


def errors():
    d = Diagram()
    d.title("Two small errors, one hidden gap")
    r = d.box("Wheel radius r\nis 1% off", 0, 0, "yellow")
    b = d.box("Track width b\nis 1% off", 0, 1, "yellow")
    x = d.box("Every distance and\nevery turn is 1% off", 1, 0, "red")
    y = d.box("Every turn is\n1% off", 1, 1, "red")
    z = d.box("Real robot ends\n0.089 m from start", 2, 0.5, "red")
    d.arrow(r, x)
    d.arrow(b, y)
    d.arrow(x, z)
    d.arrow(y, z)
    d.note("Odometry cannot see it: same wrong r and b", near=z, side="b")
    d.save(OUT / "diagram-two-errors.excalidraw")


if __name__ == "__main__":
    chain()
    errors()
