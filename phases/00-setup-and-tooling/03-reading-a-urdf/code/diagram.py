# 레슨 00/03 도해: URDF 의 kinematic tree 와 joint origin 을 어느 프레임에서 읽는지 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def tree():
    d = Diagram(cell=(280, 150))
    d.title("A URDF is a tree of links and joints")
    b = d.box("base\n(root)", 0, 0.5, "blue", w=190)
    u = d.box("upper\nvia shoulder", 1, 0.5, "blue", w=190)
    f = d.box("fore\nvia elbow", 2, 0, "blue", w=190)
    c = d.box("camera\nvia cam_mount", 2, 1, "gray", w=190)
    h = d.box("hand\nvia wrist", 3, 0, "green", w=190)
    d.arrow(b, u)
    d.arrow(u, f)
    d.arrow(u, c, dashed=True)
    d.arrow(f, h)
    d.note("Joints are the edges (shown as 'via'). Every link has one parent joint.", d.margin, d.margin + 60 + 2 * d.ch - 40, size=20)
    d.save(OUT / "diagram-urdf-tree.excalidraw")


def frames():
    d = Diagram(cell=(300, 170))
    d.title("Which frame is the origin written in?")
    a = d.box("<origin xyz=0.3 0 0>\non joint elbow", 0, 0.5, "yellow", w=250)
    ok = d.box("Parent frame\n(upper link)", 1, 0, "green", w=220)
    bad = d.box("World frame\n(what a naive sum does)", 1, 1, "red", w=250)
    r1 = d.box("Offset follows\nthe rotated link", 2, 0, "green", w=230)
    r2 = d.box("Offset ignores\nthe shoulder yaw", 2, 1, "red", w=230)
    for s, t in ((a, ok), (a, bad), (ok, r1), (bad, r2)):
        d.arrow(s, t)
    d.save(OUT / "diagram-origin-frame.excalidraw")


if __name__ == "__main__":
    tree()
    frames()
