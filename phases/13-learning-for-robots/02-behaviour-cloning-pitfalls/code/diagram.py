# 레슨 13/02 도해: 오차가 오차를 부르는 복합 오차 고리와 DAgger 재라벨링 고리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def drift():
    d = Diagram(numbered=True)
    d.title("Why small errors snowball")
    a = d.box("A bump pushes the\nrover off the demos", 0, 0, "yellow", step=1)
    b = d.box("No demo covers\nthis spot", 1, 0, "red", step=2)
    c = d.box("Steering is\na poor guess", 1, 1, "red", step=3)
    e = d.box("The next error\nis bigger", 0, 1, "red", step=4)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, label="repeats every step", dashed=True)
    d.save(OUT / "diagram-drift-loop.excalidraw")


def loop():
    d = Diagram(numbered=True)
    d.title("DAgger: label the spots the rover reaches")
    a = d.box("Rover drives\n(with wheel noise)", 0, 0, "blue", step=1)
    b = d.box("Expert labels every\nspot it reached", 1, 0, "purple", step=2)
    c = d.box("Add the pairs to\nthe data set", 1, 1, "yellow", step=3)
    e = d.box("Refit the policy", 0, 1, "green", step=4)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, label="repeat a few rounds", dashed=True)
    d.save(OUT / "diagram-dagger-loop.excalidraw")


if __name__ == "__main__":
    drift()
    loop()
