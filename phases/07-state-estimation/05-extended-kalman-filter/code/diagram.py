# 레슨 07/05 도해: EKF 가 현재 추정에서 선형화하는 순환과 나쁜 선형화점이 스스로를 악화시키는 고리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("One EKF cycle")
    a = d.box("Estimate\nx and P", col=0, row=1, color="blue")
    f = d.box("Jacobian F\nat estimate", col=1, row=0, color="purple")
    p = d.box("Predict:\nmove x, grow P", col=1, row=1, color="purple")
    h = d.box("Jacobian H\nat estimate", col=2, row=0, color="purple")
    c = d.box("Correct with\nthe landmark", col=2, row=1, color="green")
    d.arrow(f, p)
    d.arrow(a, p)
    d.arrow(h, c)
    d.arrow(p, c)
    d.arrow(c, a, label="next step")
    d.save(OUT / "diagram-ekf-loop.excalidraw")


def spiral():
    d = Diagram()
    d.title("A bad linearisation point feeds on itself")
    a = d.box("Heading off\nby a lot", col=0, row=0, color="red")
    b = d.box("Slopes taken\nat wrong spot", col=1, row=0, color="purple")
    e = d.box("Estimate gets\nworse", col=1, row=1, color="red")
    g = d.box("P stays small\n(too sure)", col=2, row=1, color="yellow")
    d.arrow(a, b)
    d.arrow(b, e)
    d.arrow(e, g)
    d.arrow(e, a, label="repeat")
    d.save(OUT / "diagram-ekf-spiral.excalidraw")


if __name__ == "__main__":
    loop()
    spiral()
