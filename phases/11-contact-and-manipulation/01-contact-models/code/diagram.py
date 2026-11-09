# 레슨 11/01 도해: 페널티 접촉 모델의 두 층과 stick/slip 판정 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def layers():
    d = Diagram()
    d.title("Two layers of a penalty contact")
    a = d.box("Penetration p\n(block into plane)", 0, 0.5, "blue")
    b = d.box("Normal force\nfn = k p + c p_dot", 1, 0, "purple")
    c = d.box("Friction cap\nmu * fn", 2, 0, "red")
    e = d.box("Tangential spring\nto an anchor", 1, 1, "yellow")
    f = d.box("Friction ft\n(clipped at the cap)", 3, 0.5, "green")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(a, e)
    d.arrow(c, f)
    d.arrow(e, f)
    d.note("The spring gives stick, the cap gives slip.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-penalty-layers.excalidraw")


def decision():
    d = Diagram(cell=(330, 170))
    d.title("Stick or slip on a tilted plane")
    t = d.box("Needed friction\nft / fn = tan(theta)", 0, 0.5, "blue", w=250)
    q = d.box("tan(theta) <= mu ?", 1, 0.5, "gray", shape="diamond", w=230, h=130)
    y = d.box("Inside the cone\nblock sticks", 2, 0, "green", w=230)
    n = d.box("Outside the cone\nblock slides", 2, 1, "red", w=230)
    d.arrow(t, q)
    d.arrow(q, y, label="yes")
    d.arrow(q, n, label="no")
    d.note("Slide acceleration = g (sin t - mu cos t)", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-stick-slip.excalidraw")


if __name__ == "__main__":
    layers()
    decision()
