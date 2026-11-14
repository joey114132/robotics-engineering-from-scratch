# 레슨 05/05 도해: fetch 작업 트리와 Sequence/Fallback 이 세 상태에 반응하는 규칙을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def tree():
    d = Diagram()
    d.title("A fetch task as a tree")
    root = d.box("Sequence\nfetch", col=0, row=1, color="purple")
    a = d.box("Go to\ncrate", col=0, row=0, color="blue")
    r = d.box("Retry\nup to 3", col=1, row=0, color="yellow")
    b = d.box("Go to\nbin", col=2, row=0, color="blue")
    g = d.box("Grasp", col=1, row=1, color="green")
    c = d.box("Release", col=2, row=1, color="blue")
    d.arrow(root, a, label="in order")
    d.arrow(a, r)
    d.arrow(r, b)
    d.arrow(b, c)
    d.arrow(r, g)
    d.save(OUT / "diagram-fetch-tree.excalidraw")


def rules():
    d = Diagram()
    d.title("What a parent does with a child's answer")
    s = d.box("Child says\nsuccess", col=0, row=0, color="green")
    f = d.box("Child says\nfailure", col=0, row=1, color="red")
    r = d.box("Child says\nrunning", col=0, row=2, color="yellow")
    a = d.box("Sequence: next child\nFallback: stop, success", col=1, row=0, color="green")
    b = d.box("Sequence: stop, failure\nFallback: next child", col=1, row=1, color="red")
    e = d.box("Both: remember this\nchild, say running", col=1, row=2, color="yellow")
    for x, y in ((s, a), (f, b), (r, e)):
        d.arrow(x, y)
    d.save(OUT / "diagram-status-rules.excalidraw")


if __name__ == "__main__":
    tree()
    rules()
