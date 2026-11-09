# 레슨 05/01 도해: QoS 요청 대 제공 판정과 keep-last 큐가 버리는 경로를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def match():
    d = Diagram(cell=(320, 170))
    d.title("A topic that connects and delivers nothing")
    p = d.box("Publisher offers\nbest effort", 0, 0, "blue", w=240)
    s = d.box("Subscriber asks\nreliable", 0, 1, "yellow", w=240)
    j = d.box("Asks more\nthan offered?", 1, 0.5, "purple", shape="diamond", w=240, h=120)
    r = d.box("No match\nno data, no crash", 2, 0.5, "red", w=240)
    d.arrow(p, j)
    d.arrow(s, j)
    d.arrow(j, r, label="yes")
    d.note("Reliable publisher + best effort subscriber is fine.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=20)
    d.save(OUT / "diagram-qos-match.excalidraw")


def queue():
    d = Diagram(cell=(310, 170))
    d.title("Depth absorbs a burst, not an overload")
    a = d.box("Publisher\n8 msgs at once", 0, 0.5, "blue", w=230)
    q = d.box("Queue\nkeep last N", 1, 0.5, "yellow", w=210)
    c = d.box("Callback\n1 msg per tick", 2, 0.5, "green", w=210)
    x = d.box("Oldest dropped\nwhen full", 1, 1.6, "red", w=230)
    d.arrow(a, q)
    d.arrow(q, c)
    d.arrow(q, x, dashed=True)
    d.save(OUT / "diagram-qos-queue.excalidraw")


if __name__ == "__main__":
    match()
    queue()
