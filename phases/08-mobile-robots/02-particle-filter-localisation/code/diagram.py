# 레슨 08/02 도해: particle filter 한 주기(예측, 가중, resampling)와 kidnapped robot 에서 고립되는 과정을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(cell=(330, 170))
    d.title("One cycle of a particle filter")
    p = d.box("Cloud of guesses\n(many poses)", 0, 0, "blue", w=240)
    a = d.box("Predict\nmove each guess + noise", 1, 0, "purple", w=270)
    b = d.box("Weight\nhow well do the ranges fit?", 2, 0, "purple", w=300)
    c = d.box("Resample\ncopy good, drop bad", 2, 1, "green", w=270)
    d.arrow(p, a)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, p, route="below")
    d.note("The pose estimate is the mean of the cloud.", d.margin, d.margin + 60 + 2 * d.ch + 110, size=20)
    d.save(OUT / "diagram-pf-cycle.excalidraw")


def kidnap():
    d = Diagram(cell=(330, 170))
    d.title("Why a collapsed cloud cannot find a moved robot")
    a = d.box("Cloud has collapsed\nonto the true pose", 0, 0.5, "green", w=250)
    b = d.box("Robot is carried\nto a new place", 1, 0.5, "yellow", w=250)
    c = d.box("Every guess fits\nthe ranges badly", 2, 0, "red", w=270)
    e = d.box("No guess is near\nthe new pose", 2, 1, "red", w=270)
    f = d.box("Add a few random\nguesses each step", 3, 0.5, "blue", w=250)
    for s, t in ((a, b), (b, c), (b, e), (c, f), (e, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-pf-kidnap.excalidraw")


if __name__ == "__main__":
    loop()
    kidnap()
