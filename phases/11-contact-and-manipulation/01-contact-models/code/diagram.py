# 레슨 11/01 도해: 경사면 위 블록이 받는 페널티 접촉의 두 층과, 25도와 35도 경사에서 stick 인지 slip 인지 가르는 판정을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def layers():
    d = Diagram()
    d.title("Two layers of a penalty contact")
    a = d.box("Block sinks a little\ninto the ramp", 0, 0, "blue")
    b = d.box("Spring-damper\nnormal force fn", 1, 0, "purple")
    c = d.box("Friction cap\nmu * fn", 2, 0, "red")
    s = d.box("Sideways spring\nholds the block", 1, 1, "yellow")
    f = d.box("Friction ft\nclipped at the cap", 2, 1, "green")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, f)
    d.arrow(s, f)
    d.note("The spring gives stick, the cap gives slip.", near=f, side="b")
    d.save(OUT / "diagram-penalty-layers.excalidraw")


def decision():
    d = Diagram()
    d.title("Stick or slip on a ramp (mu = 0.5)")
    t = d.box("Friction needed\nft / fn = tan(theta)", 0, 0.5, "blue")
    q = d.box("tan(theta)\nat most mu?", 1, 0.5, "gray")
    y = d.box("25 deg: 0.47\nblock stays", 2, 0, "green")
    n = d.box("35 deg: 0.70\nblock slides", 2, 1, "red")
    d.arrow(t, q)
    d.arrow(q, y, label="yes")
    d.arrow(q, n, label="no")
    d.note("Slide acceleration = g (sin(theta) - mu cos(theta))", near=n, side="b")
    d.save(OUT / "diagram-stick-slip.excalidraw")


if __name__ == "__main__":
    layers()
    decision()
