# 레슨 14/01 도해: 탐욕 배정이 막다른 길에 빠지는 과정과 최적 배정의 아이디어를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def trap():
    d = Diagram()
    d.title("Why greedy assignment strands a robot")
    r0 = d.box("Robot A\nnearest = task 1", 0, 0, "blue")
    r1 = d.box("Robot B\nonly task 1 is near", 0, 1, "blue")
    t = d.box("A takes task 1\nfirst", 1, 0.5, "yellow")
    s = d.box("B must drive\nfar for task 2", 2, 0.5, "red")
    g = d.box("Total cost\ngoes up", 3, 0.5, "red")
    for a, b in ((r0, t), (r1, t), (t, s), (s, g)):
        d.arrow(a, b)
    d.note("Greedy looks at one robot at a time.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-greedy-trap.excalidraw")


def optimal():
    d = Diagram(cell=(330, 170))
    d.title("Optimal assignment: pay for the swap, win overall")
    c = d.box("Cost matrix\ndistance robot to task", 0, 0.5, "blue", w=250)
    p = d.box("Potentials u, v\n(a price per row, column)", 1, 0.5, "purple", w=250)
    z = d.box("Edges with\nzero reduced cost", 2, 0, "gray", w=230)
    a = d.box("Augmenting path\nflips matches", 2, 1, "purple", w=230)
    r = d.box("Total cost is\nthe minimum", 3, 0.5, "green", w=230)
    for s, t in ((c, p), (p, z), (p, a), (z, r), (a, r)):
        d.arrow(s, t)
    d.save(OUT / "diagram-optimal-idea.excalidraw")


if __name__ == "__main__":
    trap()
    optimal()
