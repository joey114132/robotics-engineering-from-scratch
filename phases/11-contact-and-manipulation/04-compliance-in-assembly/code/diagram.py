# 레슨 11/04 도해: 딱딱한 손목이 jam 을 만드는 연쇄와 부드러운 손목이 비켜 주는 연쇄를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def jam():
    d = Diagram()
    d.title("How a stiff wrist jams the peg")
    a = d.box("Lateral offset e\nbetween tool and hole", 0, 0, "yellow")
    b = d.box("Stiff wrist turns it\ninto a big side force", 1, 0, "purple")
    c = d.box("Tip pressed on wall\nfriction grows", 2, 0, "red")
    e = d.box("Two-point wedge\ncones hold the peg", 3, 0, "red")
    f = d.box("Push cannot move it:\nJAM", 3, 1, "red")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.note("The side force is what feeds the friction.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-jam-chain.excalidraw")


def comply():
    d = Diagram(cell=(330, 170))
    d.title("A compliant wrist gives way")
    a = d.box("Same offset e", 0, 0.5, "yellow", w=200)
    b = d.box("Stiff wrist\nkx large", 1, 0, "red", w=230)
    c = d.box("Soft wrist\nkx small", 1, 1, "green", w=230)
    r = d.box("Big side force\nwedge holds: jam", 2, 0, "red", w=250)
    s = d.box("Tiny side force\npeg slides, tilt shrinks", 2, 1, "green", w=250)
    for u, v in ((a, b), (a, c), (b, r), (c, s)):
        d.arrow(u, v)
    d.save(OUT / "diagram-comply.excalidraw")


if __name__ == "__main__":
    jam()
    comply()
