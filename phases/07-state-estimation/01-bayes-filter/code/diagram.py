# 레슨 07/01 도해: Bayes filter 한 스텝(predict → update)과 dead reckoning 대 filter 의 갈림을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def cycle():
    d = Diagram()
    d.title("One step of the Bayes filter")
    a = d.box("Belief now\n(20 bars)", col=0, row=1, color="blue")
    p = d.box("Predict:\nmove + blur", col=1, row=1, color="purple")
    u = d.box("Update:\nweigh reading", col=2, row=1, color="purple")
    mv = d.box("Move\n(wheels slip)", col=1, row=0, color="yellow")
    z = d.box("Door or wall\nreading", col=2, row=0, color="yellow")
    d.arrow(a, p)
    d.arrow(p, u)
    d.arrow(mv, p)
    d.arrow(z, u)
    d.arrow(u, a, label="next belief")
    d.save(OUT / "diagram-bayes-cycle.excalidraw")


def split():
    d = Diagram()
    d.title("Why the sensor step is needed")
    s1 = d.box("Same start:\nknown cell", col=0, row=0, color="blue")
    r1 = d.box("Predict only", col=1, row=0, color="red")
    o1 = d.box("Doubt grows\nevery move", col=2, row=0, color="red")
    s2 = d.box("Same start:\nknown cell", col=0, row=1, color="blue")
    r2 = d.box("Predict +\nupdate", col=1, row=1, color="green")
    o2 = d.box("Belief stays\nnear truth", col=2, row=1, color="green")
    for x, y in ((s1, r1), (r1, o1), (s2, r2), (r2, o2)):
        d.arrow(x, y)
    d.save(OUT / "diagram-bayes-split.excalidraw")


if __name__ == "__main__":
    cycle()
    split()
