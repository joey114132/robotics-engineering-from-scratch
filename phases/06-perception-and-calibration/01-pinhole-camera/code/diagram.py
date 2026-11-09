# 레슨 06/01 도해: 3D 점이 픽셀이 되는 흐름과 깊이가 틀릴 때 점이 광선을 따라 미끄러지는 경우를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram()
    d.title("From a 3D point to a pixel and back")
    p = d.box("Point in camera frame\n(x, y, z)", 0, 0, "blue")
    u = d.box("Pixel (u, v)\nu = fx*x/z + cx", 1.2, 0, "purple", w=250)
    z = d.box("Depth z\nfrom the sensor", 0, 1, "yellow")
    b = d.box("Unproject\nx = (u - cx)*z/fx", 1.2, 1, "purple", w=250)
    r = d.box("Point again\n(only if z is right)", 2.4, 0.5, "green", w=250)
    d.arrow(p, u, label="project")
    d.arrow(u, b)
    d.arrow(z, b)
    d.arrow(b, r)
    d.note("Projection loses z. Unprojection needs it back.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-pinhole-pipeline.excalidraw")


def failure():
    d = Diagram(cell=(330, 170))
    d.title("Why a grasp target ends up centimetres off")
    a = d.box("Pixel on the\ncup rim", 0, 0.5, "blue", w=230)
    b = d.box("Depth read from\nthe table behind", 1, 0, "red", w=250)
    c = d.box("Depth read from\nthe rim itself", 1, 1, "green", w=250)
    e = d.box("Point slides along\nthe ray: off-axis\ntarget is wrong", 2, 0, "red", w=250, h=110)
    f = d.box("Target is right", 2, 1, "green", w=250)
    for s, t in ((a, b), (a, c), (b, e), (c, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-pinhole-failure.excalidraw")


if __name__ == "__main__":
    pipeline()
    failure()
