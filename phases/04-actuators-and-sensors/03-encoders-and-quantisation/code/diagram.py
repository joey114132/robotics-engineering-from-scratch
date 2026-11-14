# 레슨 04/03 도해: 축 각도가 카운트와 차분 속도로 바뀌는 과정, 필터 창 길이가 잡음과 지연을 맞바꾸는 모양을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram()
    d.title("From a turning disc to a velocity number")
    a = d.box("Disc turns smoothly", col=0, row=0, color="yellow")
    c = d.box("Reader counts\nslot edges (steps)", col=1, row=0, color="purple")
    v = d.box("Count change / dt", col=2, row=0, color="purple")
    s = d.box("Velocity jumps\nbetween 0 and one step", col=2, row=1, color="red")
    f = d.box("Window filter:\nsmooth, but late", col=1, row=1, color="blue")
    for p, q in ((a, c), (c, v), (v, s), (s, f)):
        d.arrow(p, q)
    d.note("Slow disc: most readings are 0, a few are one big step.", near=s, side="b")
    d.save(OUT / "diagram-encoder-pipeline.excalidraw")


def tradeoff():
    d = Diagram()
    d.title("Window length: smooth or fresh")
    w = d.box("Window of\nn samples", col=0, row=0.5, color="gray")
    lo = d.box("Longer n", col=1, row=0, color="blue")
    sh = d.box("Shorter n", col=1, row=1, color="blue")
    r1 = d.box("Small steps, calm\nbut n*dt/2 late", col=2, row=0, color="yellow")
    r2 = d.box("Fresh, but jumpy\nat low speed", col=2, row=1, color="red")
    for p, q in ((w, lo), (w, sh), (lo, r1), (sh, r2)):
        d.arrow(p, q)
    d.save(OUT / "diagram-window-tradeoff.excalidraw")


if __name__ == "__main__":
    pipeline()
    tradeoff()
