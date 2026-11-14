# 레슨 00/03 도해: URDF 의 kinematic tree 와 joint origin 을 어느 프레임에서 읽는지 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def tree():
    d = Diagram()
    d.title("A URDF is a tree of links and joints")
    b = d.box("base\n(root)", col=0, row=0, color="blue")
    u = d.box("upper\nvia shoulder", col=1, row=0, color="blue")
    f = d.box("fore\nvia elbow", col=2, row=0, color="blue")
    c = d.box("camera\nvia cam_mount", col=1, row=1, color="gray")
    h = d.box("hand\nvia wrist", col=2, row=1, color="green")
    for s, t in ((b, u), (u, f), (f, h)):
        d.arrow(s, t)
    d.arrow(u, c, dashed=True)
    d.note("The joint name sits on the link it leads to. Every link has one parent joint.", near=h, side="b")
    d.save(OUT / "diagram-urdf-tree.excalidraw")


def frames():
    d = Diagram()
    d.title("Which frame is the origin written in?")
    a = d.box("Elbow offset\n(0.3, 0, 0)", col=0, row=0.5, color="yellow")
    p = d.box("Parent frame\n(correct)", col=1, row=0, color="green")
    w = d.box("World frame\n(naive sum)", col=1, row=1, color="red")
    pr = d.box("Elbow at\n(0, 0.3, 0.1)", col=2, row=0, color="green")
    wr = d.box("Elbow at\n(0.3, 0, 0.1)", col=2, row=1, color="red")
    for s, t in ((a, p), (a, w), (p, pr), (w, wr)):
        d.arrow(s, t)
    d.note("The shoulder turned the parent frame by 90 degrees", near=pr, side="b")
    d.save(OUT / "diagram-origin-frame.excalidraw")


if __name__ == "__main__":
    tree()
    frames()
