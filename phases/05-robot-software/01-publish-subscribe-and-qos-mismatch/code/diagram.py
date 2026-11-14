# 레슨 05/01 도해: QoS 요청 대 제공 판정과 keep-last 큐가 버리는 경로를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def match():
    d = Diagram()
    d.title("A topic that connects and delivers nothing")
    p = d.box("Rover offers\nbest effort", col=0, row=0, color="blue")
    j = d.box("Asked for\nmore?", col=1, row=0, color="purple", shape="diamond")
    r = d.box("No match,\nno error", col=2, row=0, color="red")
    s = d.box("Arm asks for\nreliable", col=1, row=1, color="yellow")
    d.arrow(p, j)
    d.arrow(s, j)
    d.arrow(j, r, label="yes")
    d.note("A reliable rover and a best effort arm would match.", near=r, side="b")
    d.save(OUT / "diagram-qos-match.excalidraw")


def queue():
    d = Diagram()
    d.title("Depth absorbs a burst, not an overload")
    a = d.box("Rover sends\n8 messages at once", col=0, row=0.5, color="blue")
    q = d.box("Queue keeps\nthe newest N", col=1, row=0.5, color="yellow")
    c = d.box("Arm handles\n1 per tick", col=2, row=0.5, color="green")
    x = d.box("Oldest dropped\nwhen full", col=1, row=1.6, color="red")
    d.arrow(a, q)
    d.arrow(q, c)
    d.arrow(q, x, dashed=True)
    d.save(OUT / "diagram-qos-queue.excalidraw")


if __name__ == "__main__":
    match()
    queue()
