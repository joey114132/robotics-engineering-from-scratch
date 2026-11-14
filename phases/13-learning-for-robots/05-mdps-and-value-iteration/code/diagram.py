# 레슨 13/05 도해: 한 상태의 Bellman 백업과 value iteration 고리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def backup():
    d = Diagram(numbered=True)
    d.title("One tile, one backup")
    a = d.box("Rover on the tile\nright of the pit", 0, 0, "gray", step=1)
    b = d.box("Score each move:\nreward now", 1, 0, "yellow", step=2)
    c = d.box("Add gamma times\nthe next value", 2, 0, "purple", step=3)
    e = d.box("Keep the best\nmove's score", 2, 1, "blue", step=4)
    f = d.box("That is the\ntile's new value", 1, 1, "green", step=5)
    for s, t in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-bellman-backup.excalidraw")


def loop():
    d = Diagram(numbered=True)
    d.title("Sweep until nothing moves")
    z = d.box("Start: every\ntile is 0", 0, 0, "gray", step=1)
    s = d.box("Sweep: back up\nevery tile", 1, 0, "purple", step=2)
    c = d.box("Did any value\nmove much?", 2, 0, "yellow", step=3)
    p = d.box("No: pick the best\nmove per tile", 3, 0, "green", step=4)
    d.arrow(z, s)
    d.arrow(s, c)
    d.arrow(c, p, label="no")
    d.arrow(c, s, label="yes", dashed=True)
    d.note("Each sweep shrinks the error by gamma.", near=p, side="b")
    d.save(OUT / "diagram-value-iteration-loop.excalidraw")


if __name__ == "__main__":
    backup()
    loop()
