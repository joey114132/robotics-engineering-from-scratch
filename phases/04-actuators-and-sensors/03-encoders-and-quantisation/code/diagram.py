# 레슨 04/03 도해: 각도가 카운트와 차분 속도로 바뀌는 과정, 필터 창 길이의 교환을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram(cell=(300, 170))
    d.title("From shaft angle to a velocity number")
    a = d.box("Shaft angle\n(smooth)", 0, 0, "yellow", w=200)
    c = d.box("Counts\nsteps of 2*pi/CPR", 1, 0, "purple", w=230)
    v = d.box("Difference / dt", 2, 0, "purple", w=200)
    s = d.box("Velocity in steps of\n2*pi / (CPR * dt)", 3, 0, "red", w=250)
    f = d.box("Filter\nsmooth, but late", 3, 1, "blue", w=230)
    for p, q in ((a, c), (c, v), (v, s), (s, f)):
        d.arrow(p, q)
    d.note("Slow motion: the answer jumps between 0 and one step.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=20)
    d.save(OUT / "diagram-encoder-pipeline.excalidraw")


def tradeoff():
    d = Diagram(cell=(320, 170))
    d.title("Window length: smooth or fresh")
    w = d.box("Window of n samples", 0, 0.5, "gray", w=240)
    lo = d.box("Longer n", 1, 0, "blue", w=200)
    sh = d.box("Shorter n", 1, 1, "blue", w=200)
    r1 = d.box("Finer steps, less noise\nbut n*dt/2 late", 2, 0, "yellow", w=260)
    r2 = d.box("Fresh, but jumpy\nat low speed", 2, 1, "red", w=260)
    for p, q in ((w, lo), (w, sh), (lo, r1), (sh, r2)):
        d.arrow(p, q)
    d.save(OUT / "diagram-window-tradeoff.excalidraw")


if __name__ == "__main__":
    pipeline()
    tradeoff()
