# 레슨 09/05 도해: Dijkstra 와 A* 의 우선순위 차이, 휴리스틱의 약속(과소추정 금지)이 깨질 때의 결과를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def priority():
    d = Diagram()
    d.title("Same loop, one extra term in the priority")
    g = d.box("g\ncost so far", 0, 0, "blue", w=190)
    h = d.box("h\nguess to the goal", 0, 1, "yellow", w=220)
    dj = d.box("Dijkstra\nf = g", 1, 0, "gray", w=200)
    a = d.box("A*\nf = g + h", 1, 1, "purple", w=200)
    pop = d.box("Expand the cell\nwith the smallest f", 2, 0.5, "purple", w=250)
    out = d.box("Fewer cells\nlooked at", 3, 0.5, "green", w=220)
    d.arrow(g, dj)
    d.arrow(g, a)
    d.arrow(h, a)
    d.arrow(dj, pop)
    d.arrow(a, pop)
    d.arrow(pop, out)
    d.save(OUT / "diagram-astar-priority.excalidraw")


def promise():
    d = Diagram(cell=(330, 170))
    d.title("The heuristic's promise")
    k = d.box("h never guesses\nmore than the truth", 0, 0.5, "blue", w=250)
    ok = d.box("Admissible:\nA* is optimal", 1, 0, "green", w=230)
    bad = d.box("h guesses too much\n(weight w > 1)", 1, 1, "red", w=250)
    r1 = d.box("Path at most w\ntimes the best", 2, 1, "yellow", w=250)
    r2 = d.box("Dijkstra = h of 0\nthe safest guess", 2, 0, "gray", w=240)
    d.arrow(k, ok)
    d.arrow(k, bad, label="break it")
    d.arrow(ok, r2)
    d.arrow(bad, r1)
    d.save(OUT / "diagram-astar-promise.excalidraw")


if __name__ == "__main__":
    priority()
    promise()
