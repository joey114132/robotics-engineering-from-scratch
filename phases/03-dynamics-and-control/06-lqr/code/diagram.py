# 레슨 03/06 도해: 비용 Q, R 에서 게인 K 가 나오는 흐름과 R 이 주는 맞교환을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def flow():
    d = Diagram()
    d.title("LQR: say what you hate, get the gain")
    q = d.box("Q: error hurts\nR: effort hurts", 0, 0.5, "blue")
    m = d.box("Model\nx+ = A x + B u", 0, 1.5, "yellow")
    r = d.box("Riccati loop\nrepeat until P is steady", 1, 1, "purple", w=250)
    k = d.box("Gain K", 2, 1, "green", w=180)
    u = d.box("u = -K x", 3, 1, "green", w=180)
    for s, t in ((q, r), (m, r), (r, k), (k, u)):
        d.arrow(s, t)
    d.note("You tune two weights. The math tunes every entry of K.", d.margin, d.margin + 60 + 2.4 * d.ch, size=22)
    d.save(OUT / "diagram-lqr-flow.excalidraw")


def tradeoff():
    d = Diagram(cell=(330, 170))
    d.title("R sets how much effort you will pay for")
    r = d.box("Pick R", 0, 1, "gray", w=200)
    lo = d.box("R small\neffort is cheap", 1, 0, "red", w=250)
    hi = d.box("R large\neffort is costly", 1, 2, "blue", w=250)
    a = d.box("Fast, big peak input,\nmay saturate", 2, 0, "red", w=270)
    b = d.box("Slow, gentle,\nsmall peak input", 2, 2, "blue", w=270)
    for s, t in ((r, lo), (r, hi), (lo, a), (hi, b)):
        d.arrow(s, t)
    d.save(OUT / "diagram-lqr-tradeoff.excalidraw")


if __name__ == "__main__":
    flow()
    tradeoff()
