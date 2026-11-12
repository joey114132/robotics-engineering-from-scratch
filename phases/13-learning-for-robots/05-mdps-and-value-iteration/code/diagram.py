# 레슨 13/05 도해: 한 상태의 Bellman 백업과 value iteration 고리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def backup():
    d = Diagram(cell=(330, 170))
    d.title("One state, one backup")
    s = d.box("State s", 0, 0.5, "gray", w=170)
    a = d.box("Try each action:\nreward now", 1, 0, "yellow", w=250)
    b = d.box("Plus gamma times the\nvalue of where it leads", 1, 1, "purple", w=250)
    m = d.box("Keep the\nbest action", 2, 0.5, "blue", w=200)
    v = d.box("New V(s)", 3, 0.5, "green", w=170)
    for x, y in ((s, a), (s, b), (a, m), (b, m), (m, v)):
        d.arrow(x, y)
    d.save(OUT / "diagram-bellman-backup.excalidraw")


def loop():
    d = Diagram(cell=(310, 170))
    d.title("Value iteration: sweep until nothing moves")
    z = d.box("Start: V = 0\neverywhere", 0, 0, "gray", w=210)
    s = d.box("Sweep: back up\nevery state", 1, 0, "purple", w=210)
    c = d.box("Change below\ntolerance?", 2, 0, "yellow", w=210, shape="diamond")
    f = d.box("Fixed point V*", 3, 0, "green", w=190)
    p = d.box("Greedy policy:\nbest action", 3, 1, "blue", w=210)
    d.arrow(z, s)
    d.arrow(s, c)
    d.arrow(c, f, label="yes")
    d.arrow(c, s, label="no", route="below", dashed=True)
    d.arrow(f, p)
    d.note("Each sweep shrinks the error by gamma.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-value-iteration-loop.excalidraw")


if __name__ == "__main__":
    backup()
    loop()
