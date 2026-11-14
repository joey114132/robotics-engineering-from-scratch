# 레슨 09/05 도해: Dijkstra 와 A* 의 우선순위 차이, 휴리스틱의 약속(과대추정 금지)이 깨질 때의 결과를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def priority():
    d = Diagram()
    d.title("Same loop, one extra term")
    g = d.box("g: steps\nspent so far", 0, 0, "blue")
    h = d.box("h: guessed\nsteps left", 1, 0, "yellow")
    f = d.box("Priority f = g + h\n(Dijkstra: f = g)", 0, 1, "purple")
    e = d.box("Expand the\ncell with lowest f", 0, 2, "purple")
    r = d.box("A* looks at fewer\ncells (115, not 153)", 0, 3, "green")
    d.arrow(g, f)
    d.arrow(h, f)
    d.arrow(f, e)
    d.arrow(e, r)
    d.save(OUT / "diagram-astar-priority.excalidraw")


def promise():
    d = Diagram()
    d.title("The heuristic's promise")
    a = d.box("h never\noverestimates", 0, 0, "blue")
    b = d.box("h guesses too\nmuch (w = 4)", 1, 0, "red")
    ok = d.box("A* walk\ncosts 26", 0, 1, "green")
    bad = d.box("Walk costs 36,\nnot 26", 1, 1, "red")
    z = d.box("h = 0 is\nDijkstra, safest", 0, 2, "gray")
    bound = d.box("Never worse than\nw times the best", 1, 2, "yellow")
    d.arrow(a, ok)
    d.arrow(b, bad)
    d.arrow(ok, z)
    d.arrow(bad, bound)
    d.save(OUT / "diagram-astar-promise.excalidraw")


if __name__ == "__main__":
    priority()
    promise()
