# 레슨 15/02 도해: 하트비트가 watchdog 을 거쳐 정지로 이어지는 흐름과 정지 거리 예산을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def flow():
    d = Diagram()
    d.title("A heartbeat keeps the joint allowed to move")
    src = d.box("Program\nsends commands", col=0, row=0, color="blue")
    loop = d.box("Arm joint\nkeeps the last command", col=1, row=0, color="yellow")
    wd = d.box("Watchdog\nno heartbeat for T?", col=0, row=1, color="purple")
    stop = d.box("Stop action\nbrake to rest", col=1, row=1, color="green")
    d.arrow(src, loop, label="command")
    d.arrow(src, wd, label="heartbeat", dashed=True)
    d.arrow(wd, stop, label="trip")
    d.arrow(stop, loop, label="takes over")
    d.note("If the program crashes, the heartbeat stops and the watchdog trips.", d.margin, d.margin + 60 + 2 * d.ch)
    d.save(OUT / "diagram-watchdog-flow.excalidraw")
    return d


def budget():
    d = Diagram(numbered=True)
    d.title("The distance budget after the program dies")
    a = d.box("Program dies\narm at speed v", col=0, row=0, color="red")
    b = d.box("Timeout T\narm travels v * T", col=1, row=0, color="yellow")
    c = d.box("Braking\narm travels v^2 / 2a", col=2, row=0, color="purple")
    e = d.box("At rest\nbefore the stop", col=3, row=0, color="green")
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.note("v * T + v^2 / (2a) <= room to the stop, so T <= (room - v^2 / 2a) / v", d.margin, d.margin + 60 + 2 * d.ch)
    d.save(OUT / "diagram-stop-budget.excalidraw")
    return d


if __name__ == "__main__":
    for dd in (flow(), budget()):
        print(dd.warnings)
