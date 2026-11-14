# 레슨 09/04 도해: 비용 두 항과 gradient descent 루프, 웨이포인트에 걸리는 두 힘을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(numbered=True)
    d.title("Smooth the route by lowering a cost")
    w = d.box("Waypoints,\nends pinned", 0, 0, "blue", step=1)
    c = d.box("Cost: smoothness\n+ cup penalty", 1, 0, "purple", step=2)
    g = d.box("Gradient: where\ncost rises fastest", 1, 1, "purple", step=3)
    s = d.box("Step against it,\nmove waypoints", 0, 1, "green", step=4)
    d.arrow(w, c)
    d.arrow(c, g)
    d.arrow(g, s)
    d.arrow(s, w, dashed=True, label="repeat")
    d.save(OUT / "diagram-cost-loop.excalidraw")


def forces():
    d = Diagram()
    d.title("Two forces on every waypoint")
    n = d.box("Neighbours pull\nthe band straight", 0, 0, "blue")
    o = d.box("Cup pushes it\nout of the margin", 1, 0, "red")
    b = d.box("Balance:\nsmooth and clear", 0, 1, "green")
    g = d.box("Small step:\ncost goes down", 0, 2, "green")
    t = d.box("Step too big:\ncost goes up", 1, 2, "red")
    d.arrow(n, b)
    d.arrow(o, b)
    d.arrow(b, g)
    d.arrow(g, t, dashed=True, label="raise the step")
    d.save(OUT / "diagram-two-forces.excalidraw")


if __name__ == "__main__":
    loop()
    forces()
