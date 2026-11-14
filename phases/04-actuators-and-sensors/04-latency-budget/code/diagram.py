# 레슨 04/04 도해: 제어 루프 한 바퀴의 단계별 지연을 더한 예산, 그리고 지연이 phase margin 을 소모해 kd 상한을 낮추는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def budget():
    d = Diagram(numbered=True)
    d.title("Delay budget of one loop")
    s = d.box("Sensor read\n0.5 ms", col=0, row=0, color="yellow", step=1)
    f = d.box("Velocity filter\n2 ms", col=1, row=0, color="yellow", step=2)
    b = d.box("Bus transfer\n1 ms", col=2, row=0, color="yellow", step=3)
    c = d.box("Compute\n0.5 ms", col=2, row=1, color="yellow", step=4)
    a = d.box("Drive latch\n1 ms", col=1, row=1, color="yellow", step=5)
    h = d.box("Hold\nhalf a period\n0.5 ms", col=0, row=1, color="purple", step=6)
    t = d.box("Total\n5.5 ms", col=0, row=2, color="red", step=7)
    for p, q in ((s, f), (f, b), (b, c), (c, a), (a, h), (h, t)):
        d.arrow(p, q)
    d.note("Made-up numbers. Delays add.", near=t, side="r")
    d.save(OUT / "diagram-latency-budget.excalidraw")


def margin():
    d = Diagram(numbered=True)
    d.title("Delay spends the phase margin")
    pm = d.box("The PD loop starts\nwith a margin PM", col=0, row=0, color="green", step=1)
    lag = d.box("Delay T adds\nlag wc * T", col=1, row=0, color="red", step=2)
    left = d.box("Margin left\nPM - wc*T", col=2, row=0, color="purple", step=3)
    bad = d.box("Zero or less:\nthe arm oscillates", col=2, row=1, color="red", step=4)
    fix = d.box("Fix: lower kd,\nlower crossover wc", col=1, row=1, color="blue", step=5)
    for p, q in ((pm, lag), (lag, left), (left, bad), (bad, fix)):
        d.arrow(p, q)
    d.save(OUT / "diagram-delay-margin.excalidraw")


if __name__ == "__main__":
    budget()
    margin()
