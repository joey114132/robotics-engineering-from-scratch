# 레슨 07/02 도해: Kalman filter 의 predict-correct 순환과 gain 이 신뢰를 나누는 방식을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("One Kalman cycle")
    a = d.box("Last estimate\nx and P", col=0, row=1, color="blue")
    p = d.box("Predict:\nP grows by Q", col=1, row=1, color="purple")
    c = d.box("Correct with\ngain K", col=2, row=1, color="green")
    z = d.box("Position\nreading z", col=2, row=0, color="yellow")
    d.arrow(a, p)
    d.arrow(p, c)
    d.arrow(z, c)
    d.arrow(c, a, label="next step")
    d.save(OUT / "diagram-kalman-loop.excalidraw")


def trust():
    d = Diagram()
    d.title("The gain is a trust dial")
    r = d.box("Noisy sensor\n(R is big)", col=0, row=0, color="red")
    k1 = d.box("K near 0", col=1, row=0, color="purple")
    o1 = d.box("Follow\nthe model", col=2, row=0, color="green")
    p = d.box("Unsure model\n(P is big)", col=0, row=1, color="blue")
    k2 = d.box("K near 1", col=1, row=1, color="purple")
    o2 = d.box("Follow\nthe sensor", col=2, row=1, color="green")
    for x, y in ((r, k1), (k1, o1), (p, k2), (k2, o2)):
        d.arrow(x, y)
    d.save(OUT / "diagram-kalman-trust.excalidraw")


if __name__ == "__main__":
    loop()
    trust()
