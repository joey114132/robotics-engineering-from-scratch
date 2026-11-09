# 레슨 16/02 도해: 내비게이션 시스템 구성도와 오도메트리 오차가 landmark 보정으로 복구되는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def system():
    d = Diagram()
    d.title("Navigation: which lesson each part comes from")
    g = d.box("Occupancy grid\nlesson 08/03", 0, 0, "blue")
    a = d.box("A* search\nnew here", 1, 0, "purple")
    s = d.box("Shortcut smoothing\nlesson 09/03", 2, 0, "purple")
    p = d.box("Pure pursuit\nlesson 08/04", 2, 1, "purple")
    r = d.box("Differential drive\nlesson 08/01", 1, 1, "yellow")
    o = d.box("Odometry estimate\n+ landmark fix", 0, 1, "gray")
    for x, y in ((g, a), (a, s), (s, p), (p, r), (r, o)):
        d.arrow(x, y)
    d.note("The pose estimate goes back into pure pursuit. The grid is inflated by the robot radius first.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=18)
    d.save(OUT / "diagram-nav-system.excalidraw")


def broken():
    d = Diagram()
    d.title("Break test: raise the odometry error")
    a = d.box("Odometry error\nraised", 0, 0, "gray")
    b = d.box("Estimate drifts\naway from truth", 1, 0, "red")
    c = d.box("Robot follows\nthe wrong path", 2, 0, "red")
    e = d.box("Wall hit,\ngoal missed", 2, 1, "red")
    f = d.box("Landmark fix\nresets the pose", 1, 1, "green")
    h = d.box("Back on the path,\ngoal reached", 0, 1, "green")
    for x, y in ((a, b), (b, c), (c, e)):
        d.arrow(x, y)
    d.arrow(f, h)
    d.arrow(b, f, dashed=True, label="fix", label_dx=26)
    d.note("Red path: no fix. Green path: the fix keeps the error small.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=18)
    d.save(OUT / "diagram-nav-broken.excalidraw")


if __name__ == "__main__":
    system()
    broken()
