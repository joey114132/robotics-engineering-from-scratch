# 레슨 03/06 도해: 비용 Q, R 에서 게인 K 가 나오는 흐름과 R 이 주는 맞교환을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def flow():
    d = Diagram(numbered=True)
    d.title("LQR: say what you hate, get the gain")
    q = d.box("Q: error hurts\nR: effort hurts", 0, 0, "blue", step=1)
    m = d.box("Car model\nx+ = A x + B u", 1, 0, "yellow", step=2)
    r = d.box("Riccati loop,\nuntil P is steady", 0.5, 1, "purple", step=3)
    k = d.box("Gain K", 0.5, 2, "green", step=4)
    u = d.box("Push: u = -K x", 0.5, 3, "green", step=5)
    for s, t in ((q, r), (m, r), (r, k), (k, u)):
        d.arrow(s, t)
    d.note("You tune two weights. The math tunes every entry of K.", near=u, side="b")
    d.save(OUT / "diagram-lqr-flow.excalidraw")


def tradeoff():
    d = Diagram()
    d.title("R sets how much effort you will pay for")
    r = d.box("Pick R", 0.5, 0, "gray")
    lo = d.box("R small (0.01):\neffort is cheap", 0, 1, "red")
    hi = d.box("R large (10):\neffort is costly", 1, 1, "blue")
    a = d.box("Fast, first push\n8.7, may saturate", 0, 2, "red")
    b = d.box("Slow, gentle,\nfirst push 0.3", 1, 2, "blue")
    for s, t in ((r, lo), (r, hi), (lo, a), (hi, b)):
        d.arrow(s, t)
    d.save(OUT / "diagram-lqr-tradeoff.excalidraw")


if __name__ == "__main__":
    flow()
    tradeoff()
