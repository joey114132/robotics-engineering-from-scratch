# 레슨 00/04 도해: ROS 2 의 node, topic, service 관계와 queue depth 가 있는 subscriber 경로를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def parts():
    d = Diagram()
    d.title("Nodes talk over topics and services")
    cam = d.box("camera\nnode", col=0, row=0, color="yellow")
    top = d.box("topic\n/cup_position", col=1, row=0, color="purple")
    ctl = d.box("arm\nnode", col=2, row=0, color="blue")
    op = d.box("operator\nnode", col=0, row=1, color="yellow")
    srv = d.box("service\n/set_mode", col=1, row=1, color="purple")
    drv = d.box("driver\nnode", col=2, row=1, color="blue")
    d.arrow(cam, top, label="publish")
    d.arrow(top, ctl, label="subscribe")
    d.arrow(op, srv, label="request")
    d.arrow(srv, drv)
    d.arrow(drv, op, label="reply", dashed=True, route="below")
    d.note("Topic: a stream, no reply. Service: one request, one reply.", near=ctl, side="b")
    d.save(OUT / "diagram-ros-parts.excalidraw")


def queue():
    d = Diagram()
    d.title("A slow subscriber and a short queue")
    p = d.box("camera\n100/s", col=0, row=0, color="yellow")
    q = d.box("queue\ndepth N", col=1, row=0, color="purple")
    s = d.box("arm\nreads 40/s", col=2, row=0, color="blue")
    x = d.box("oldest report\nis dropped", col=1, row=1, color="red")
    d.arrow(p, q)
    d.arrow(q, s)
    d.arrow(q, x, dashed=True, label="queue full")
    d.note("keeps the newest N reports", near=q, side="t")
    d.save(OUT / "diagram-queue-depth.excalidraw")


if __name__ == "__main__":
    parts()
    queue()
