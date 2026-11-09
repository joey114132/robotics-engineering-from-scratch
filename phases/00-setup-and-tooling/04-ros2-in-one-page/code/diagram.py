# 레슨 00/04 도해: ROS 2 의 node, topic, service 관계와 queue depth 가 있는 subscriber 경로를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def parts():
    d = Diagram(cell=(310, 150))
    d.title("Nodes talk over topics and services")
    a = d.box("driver node", 0, 0, "yellow", w=200)
    t = d.box("topic\n/joint_states", 1, 0, "purple", w=210)
    b = d.box("controller node", 2, 0, "blue", w=210)
    c = d.box("client node", 0, 1.2, "yellow", w=200)
    s = d.box("service\n/set_mode", 1, 1.2, "purple", w=210)
    e = d.box("server node", 2, 1.2, "blue", w=210)
    d.arrow(a, t, label="publish")
    d.arrow(t, b, label="subscribe")
    d.arrow(c, s, label="request")
    d.arrow(s, e)
    d.arrow(e, c, route="below", label="reply", dashed=True)
    d.note("Topic: many messages, no reply.  Service: one request, one reply.", d.margin, d.margin + 60 + 2.2 * d.ch + 60, size=20)
    d.save(OUT / "diagram-ros-parts.excalidraw")


def queue():
    d = Diagram(cell=(310, 170))
    d.title("A slow subscriber and a short queue")
    p = d.box("publisher\n100 per second", 0, 0.5, "yellow", w=210)
    q = d.box("queue, depth N\nkeeps the last N", 1, 0.5, "purple", w=240)
    s = d.box("subscriber\n40 per second", 2, 0.5, "blue", w=210)
    x = d.box("oldest message\nis dropped when full", 1, 1.6, "red", w=260)
    d.arrow(p, q)
    d.arrow(q, s)
    d.arrow(q, x, dashed=True)
    d.save(OUT / "diagram-queue-depth.excalidraw")


if __name__ == "__main__":
    parts()
    queue()
