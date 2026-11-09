# 레슨 04/04 도해: 제어 루프의 단계별 지연 예산, 그리고 지연이 phase margin 을 소모해 kd 를 낮추게 만드는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def budget():
    d = Diagram(cell=(250, 170))
    d.title("Latency budget of one control loop")
    s = d.box("Sensor read\n0.5 ms", 0, 0, "yellow", w=190)
    f = d.box("Velocity filter\n2 ms", 1, 0, "yellow", w=190)
    b = d.box("Bus transfer\n1 ms", 2, 0, "yellow", w=190)
    c = d.box("Compute\n0.5 ms", 3, 0, "yellow", w=190)
    a = d.box("Drive latch\n1 ms", 4, 0, "yellow", w=190)
    h = d.box("Hold: half a\n1 ms period = 0.5 ms", 2, 1, "purple", w=270)
    t = d.box("Total 5.5 ms", 3.5, 1, "red", w=200)
    for p, q in ((s, f), (f, b), (b, c), (c, a)):
        d.arrow(p, q)
    d.arrow(h, t)
    d.note("Illustrative numbers for one made-up loop, not a datasheet. Delays add.", d.margin, d.margin + 60 + 2 * d.ch - 30, size=20)
    d.save(OUT / "diagram-latency-budget.excalidraw")


def margin():
    d = Diagram(cell=(300, 170))
    d.title("Delay spends the phase margin")
    pm = d.box("PD gives phase margin", 0, 0, "green", w=250)
    lag = d.box("Delay T adds lag\nwc * T", 1, 0, "red", w=230)
    left = d.box("Margin left\nPM - wc*T", 2, 0, "purple", w=210)
    bad = d.box("Zero or less:\nloop oscillates", 3, 0, "red", w=210)
    fix = d.box("Fix: lower kd,\nlower crossover wc", 3, 1, "blue", w=240)
    for p, q in ((pm, lag), (lag, left), (left, bad)):
        d.arrow(p, q)
    d.arrow(bad, fix)
    d.save(OUT / "diagram-delay-margin.excalidraw")


if __name__ == "__main__":
    budget()
    margin()
