# 레슨 07/02 도해: Kalman filter 의 predict-correct 순환과 gain 이 신뢰를 나누는 방식을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("One Kalman cycle")
    a = d.box("Last estimate\nx and P", 0, 1, "blue", w=200)
    p = d.box("Predict\nP grows by Q", 1, 1, "purple", w=220)
    k = d.box("Gain K\nhow much to trust z", 2, 1, "purple", w=240)
    c = d.box("Correct\nx moves, P shrinks", 3, 1, "green", w=230)
    z = d.box("Position\nreading z", 2, 0, "yellow", w=200)
    d.arrow(a, p)
    d.arrow(p, k)
    d.arrow(k, c)
    d.arrow(z, k)
    d.arrow(c, a, route="below", label="next step")
    d.save(OUT / "diagram-kalman-loop.excalidraw")


def trust():
    d = Diagram(cell=(330, 170))
    d.title("The gain is a trust dial")
    r = d.box("Noisy sensor\nR is big", 0, 0, "red", w=230)
    p = d.box("Unsure model\nP is big", 0, 1, "blue", w=230)
    k1 = d.box("K near 0", 1, 0, "purple", w=190)
    k2 = d.box("K near 1", 1, 1, "purple", w=190)
    o1 = d.box("Follow the\nmodel", 2, 0, "green", w=220)
    o2 = d.box("Follow the\nsensor", 2, 1, "green", w=220)
    for x, y in ((r, k1), (p, k2), (k1, o1), (k2, o2)):
        d.arrow(x, y)
    d.note("K = P / (P + R) for one number", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-kalman-trust.excalidraw")


if __name__ == "__main__":
    loop()
    trust()
