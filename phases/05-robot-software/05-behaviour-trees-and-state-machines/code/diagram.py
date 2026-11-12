# 레슨 05/05 도해: fetch 작업 트리와 Sequence/Fallback 이 세 상태에 반응하는 규칙을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def tree():
    d = Diagram(cell=(280, 170))
    d.title("A fetch task as a tree")
    root = d.box("Sequence\nfetch", 1.5, 0, "purple", w=220)
    a = d.box("Go to\nobject", 0, 1.3, "blue", w=190)
    r = d.box("Retry x3", 1, 1.3, "yellow", w=190)
    b = d.box("Go to\nbin", 2, 1.3, "blue", w=190)
    c = d.box("Release", 3, 1.3, "blue", w=190)
    g = d.box("Grasp", 1, 2.6, "green", w=190)
    for t in (a, r, b, c):
        d.arrow(root, t)
    d.arrow(r, g)
    d.save(OUT / "diagram-fetch-tree.excalidraw")


def rules():
    d = Diagram(cell=(330, 170))
    d.title("What a parent does with a child's answer")
    c = d.box("Child says", 0, 1, "gray", w=200)
    s = d.box("Success", 1, 0, "green", w=180)
    f = d.box("Failure", 1, 1, "red", w=180)
    r = d.box("Running", 1, 2, "yellow", w=180)
    a = d.box("Sequence: next child\nFallback: stop, success", 2, 0, "green", w=300, size=18)
    b = d.box("Sequence: stop, failure\nFallback: next child", 2, 1, "red", w=300, size=18)
    e = d.box("Both: stop, remember\nthis child, say running", 2, 2, "yellow", w=300, size=18)
    for t in (s, f, r):
        d.arrow(c, t)
    for x, y in ((s, a), (f, b), (r, e)):
        d.arrow(x, y)
    d.save(OUT / "diagram-status-rules.excalidraw")


if __name__ == "__main__":
    tree()
    rules()
