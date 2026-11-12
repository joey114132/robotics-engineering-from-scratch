# 레슨 07/05 도해: EKF 가 현재 추정에서 선형화하는 순환과 나쁜 선형화점이 스스로를 악화시키는 고리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("One EKF cycle: linearise where you think you are")
    a = d.box("Estimate\nx and P", 0, 1, "blue", w=200)
    f = d.box("Jacobian F\nat the estimate", 1, 0, "purple", w=230)
    p = d.box("Predict\nmove x, grow P", 1, 1, "purple", w=230)
    h = d.box("Jacobian H\nat the estimate", 2, 0, "purple", w=230)
    z = d.box("Range and\nbearing", 2, 1, "yellow", w=200)
    c = d.box("Correct\nx moves, P shrinks", 3, 1, "green", w=230)
    d.arrow(a, f)
    d.arrow(a, p)
    d.arrow(f, p)
    d.arrow(h, c)
    d.arrow(z, c)
    d.arrow(c, a, route="below", label="next step")
    d.save(OUT / "diagram-ekf-loop.excalidraw")


def spiral():
    d = Diagram(cell=(330, 170))
    d.title("A bad linearisation point feeds on itself")
    a = d.box("Heading guess\nis far off", 0, 1, "red", w=230)
    b = d.box("Jacobian is built\nat the wrong place", 1, 0, "purple", w=250)
    e = d.box("Estimate is\nmore wrong", 2, 1, "red", w=220)
    g = d.box("Covariance still\nsmall: overconfident", 3, 1, "yellow", w=250)
    d.arrow(a, b)
    d.arrow(b, e)
    d.arrow(e, g)
    d.arrow(e, a, route="below", label="repeat")
    d.save(OUT / "diagram-ekf-spiral.excalidraw")


if __name__ == "__main__":
    loop()
    spiral()
