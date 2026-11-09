# 레슨 07/01 도해: Bayes filter 한 스텝(predict → update)과 dead reckoning 대 filter 의 갈림을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def cycle():
    d = Diagram()
    d.title("One step of the Bayes filter")
    a = d.box("Belief\nbefore", 0, 0, "blue", w=190)
    p = d.box("Predict\nmotion blurs it", 1, 0, "purple", w=230)
    u = d.box("Update\nsensor sharpens it", 2, 0, "purple", w=230)
    b = d.box("Belief\nafter", 3, 0, "green", w=190)
    mv = d.box("Move command\n(not exact)", 1, 1, "yellow", w=230)
    z = d.box("Door or wall\nreading (noisy)", 2, 1, "yellow", w=230)
    d.arrow(a, p)
    d.arrow(p, u)
    d.arrow(u, b)
    d.arrow(mv, p)
    d.arrow(z, u)
    d.note("Predict adds doubt. Update removes it.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-bayes-cycle.excalidraw")


def split():
    d = Diagram(cell=(330, 170))
    d.title("Why the sensor step is not optional")
    s = d.box("Robot knows\nits start cell", 0, 0.5, "blue", w=230)
    r1 = d.box("Predict only\n(dead reckoning)", 1, 0, "red", w=250)
    r2 = d.box("Predict + update\n(Bayes filter)", 1, 1, "green", w=250)
    o1 = d.box("Spread grows\n+0.1 cell^2 per step", 2, 0, "red", w=260)
    o2 = d.box("Belief stays\nnear the truth", 2, 1, "green", w=260)
    for x, y in ((s, r1), (s, r2), (r1, o1), (r2, o2)):
        d.arrow(x, y)
    d.save(OUT / "diagram-bayes-split.excalidraw")


if __name__ == "__main__":
    cycle()
    split()
