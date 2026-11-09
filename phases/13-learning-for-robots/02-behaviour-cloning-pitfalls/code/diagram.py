# 레슨 13/02 도해: 오차가 오차를 부르는 복합 오차 고리와 DAgger 재라벨링 고리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def drift():
    d = Diagram(cell=(310, 170))
    d.title("Why small errors snowball")
    a = d.box("Small action error", 0, 0.5, "yellow", w=230)
    b = d.box("Next state is off\nthe demo path", 1, 0.5, "red", w=230)
    c = d.box("Policy never saw\nthis state", 2, 0.5, "red", w=230)
    e = d.box("Bigger error", 3, 0.5, "red", w=200)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, b, route="below", label="repeats every step", dashed=True)
    d.save(OUT / "diagram-drift-loop.excalidraw")


def loop():
    d = Diagram(cell=(310, 170))
    d.title("DAgger: label the states the learner visits")
    a = d.box("Learner drives\n(with noise)", 0, 0, "blue", w=230)
    b = d.box("Expert labels\nevery visited state", 1, 0, "purple", w=230)
    c = d.box("Add to the\ndata set", 2, 0, "yellow", w=210)
    e = d.box("Refit the policy", 3, 0, "green", w=210)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, route="below", label="repeat for a few rounds", dashed=True)
    d.save(OUT / "diagram-dagger-loop.excalidraw")


if __name__ == "__main__":
    drift()
    loop()
