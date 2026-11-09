# 레슨 09/04 도해: 비용 두 항과 gradient descent 루프, 웨이포인트에 걸리는 두 힘을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(cell=(330, 170))
    d.title("Smooth the path by descending a cost")
    w = d.box("Waypoints\nstart fixed, end fixed", 0, 1, "blue", w=250)
    s = d.box("Smoothness cost\nsum of squared steps", 1, 0, "purple", w=250)
    o = d.box("Obstacle penalty\nnear each circle", 1, 1, "purple", w=250)
    g = d.box("Gradient step\nmove the waypoints", 2, 1, "green", w=250)
    d.arrow(w, s)
    d.arrow(w, o)
    d.arrow(s, g)
    d.arrow(o, g)
    d.arrow(g, w, route="below", dashed=True, label="repeat", label_dy=14)
    d.save(OUT / "diagram-cost-loop.excalidraw")


def forces():
    d = Diagram()
    d.title("Two forces on every waypoint")
    n = d.box("Neighbours pull\nit onto a line", 0, 0, "blue")
    o = d.box("Obstacle pushes\nit out of the margin", 0, 1, "red")
    b = d.box("Balance:\nsmooth and clear", 1, 0.5, "green")
    g = d.box("Small step:\ncost goes down", 2, 0.5, "green")
    t = d.box("Step too big:\ncost goes up", 2, 1.5, "red")
    d.arrow(n, b)
    d.arrow(o, b)
    d.arrow(b, g)
    d.arrow(g, t, dashed=True, label="raise the step")
    d.save(OUT / "diagram-two-forces.excalidraw")


if __name__ == "__main__":
    loop()
    forces()
