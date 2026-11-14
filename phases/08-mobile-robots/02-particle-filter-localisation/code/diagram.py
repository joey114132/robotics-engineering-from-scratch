# 레슨 08/02 도해: particle filter 한 주기(예측, 가중, resampling)와 kidnapped robot 에서 고립되는 과정을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(numbered=True)
    d.title("One cycle of a particle filter")
    p = d.box("Cloud of guesses\n1000 poses", 0, 0, "blue", step=1)
    a = d.box("Predict\nmove each guess + noise", 1, 0, "purple", step=2)
    b = d.box("Weight\ndo distances to posts fit?", 1, 1, "purple", step=3)
    c = d.box("Resample\ncopy good, drop bad", 0, 1, "green", step=4)
    d.arrow(p, a)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, p)
    d.note("estimate = mean of the cloud", near=c, side="b")
    d.save(OUT / "diagram-pf-cycle.excalidraw")


def kidnap():
    d = Diagram(numbered=True)
    d.title("Why a collapsed cloud stays lost")
    a = d.box("Cloud has collapsed\nonto the rover", 0, 0, "green", step=1)
    b = d.box("Rover is carried\nto another corner", 1, 0, "yellow", step=2)
    c = d.box("Every guess is far\nfrom the new spot", 2, 0, "red", step=3)
    e = d.box("Copying them keeps\nthe cloud at the old spot", 2, 1, "red", step=4)
    f = d.box("Random guesses:\nsome land near it", 1, 1, "blue", step=5)
    for s_, t in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(s_, t)
    d.save(OUT / "diagram-pf-kidnap.excalidraw")


if __name__ == "__main__":
    loop()
    kidnap()
