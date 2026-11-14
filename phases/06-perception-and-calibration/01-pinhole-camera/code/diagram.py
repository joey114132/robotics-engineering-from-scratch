# 레슨 06/01 도해: 3D 점이 픽셀이 되는 흐름과 깊이가 틀릴 때 점이 광선을 따라 미끄러지는 경우를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram()
    d.title("From the cup rim to a pixel and back")
    p = d.box("Cup rim\n(x, y, z)", col=0, row=0, color="blue")
    u = d.box("Pixel (u, v)\nu = fx*x/z + cx", col=1, row=0, color="purple")
    z = d.box("Depth z\nfrom the sensor", col=0, row=1, color="yellow")
    b = d.box("Unproject\nx = (u - cx)*z/fx", col=1, row=1, color="purple")
    r = d.box("Point again\nonly if z is right", col=2, row=1, color="green")
    d.arrow(p, u, label="project")
    d.arrow(u, b)
    d.arrow(z, b)
    d.arrow(b, r)
    d.note("depth is lost here", near=u, side="r")
    d.save(OUT / "diagram-pinhole-pipeline.excalidraw")
    return d.warnings


def failure():
    d = Diagram()
    d.title("Why the arm misses the cup")
    a = d.box("Pixel on\nthe cup rim", col=0, row=0.5, color="blue")
    b = d.box("Wall's depth\n1.15 m", col=1, row=0, color="red")
    c = d.box("Rim's depth\n1.00 m", col=1, row=1, color="green")
    e = d.box("5 cm beside\nthe cup: miss", col=2, row=0, color="red")
    f = d.box("On the cup:\ngrasp", col=2, row=1, color="green")
    for s, t in ((a, b), (a, c), (b, e), (c, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-pinhole-failure.excalidraw")
    return d.warnings


if __name__ == "__main__":
    print(pipeline(), failure())
