# 레슨 15/02 도해: 하트비트가 watchdog 을 거쳐 정지로 이어지는 흐름과 정지 거리 예산을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def flow():
    d = Diagram(cell=(300, 170))
    d.title("A heartbeat keeps the joint allowed to move")
    src = d.box("Command source\nplanner or UI", 0, 0, "blue", w=220)
    loop = d.box("Joint loop\nlatches last command", 1, 0, "yellow", w=240)
    wd = d.box("Watchdog\nsilence > timeout?", 1, 1.3, "purple", w=240)
    stop = d.box("Stop action\nramp to rest", 2, 1.3, "green", w=220)
    d.arrow(src, loop, label="command")
    d.arrow(src, wd, label="heartbeat", dashed=True, label_dy=-10)
    d.arrow(wd, stop, label="trip")
    d.arrow(stop, loop, label="takes over")
    d.save(OUT / "diagram-watchdog-flow.excalidraw")


def budget():
    d = Diagram(cell=(300, 170))
    d.title("The distance budget after the source dies")
    a = d.box("Source dies\nat speed v", 0, 0, "red", w=210)
    b = d.box("Timeout T\ntravel v * T", 1, 0, "yellow", w=210)
    c = d.box("Braking\ntravel v^2 / 2a", 2, 0, "purple", w=210)
    e = d.box("At rest\nbefore the limit", 3, 0, "green", w=210)
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.note("v * T + v^2 / (2a) <= room to the limit,  so  T <= (room - v^2 / 2a) / v", d.margin, d.margin + 60 + d.ch - 10, size=22)
    d.save(OUT / "diagram-stop-budget.excalidraw")


if __name__ == "__main__":
    flow()
    budget()
