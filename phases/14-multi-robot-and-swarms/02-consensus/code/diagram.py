# 레슨 14/02 도해: 로봇 하나의 합의 갱신과, 느린 고유 모드가 속도를 정하는 이유를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def update():
    d = Diagram(numbered=True)
    d.title("One car on the ring: step toward your neighbours")
    n = d.box("See neighbours\nx = 2 and x = 0", 0, 0, "blue")
    df = d.box("Differences x_j - x_i\n-5 and -7", 1, 0, "purple")
    st = d.box("Small step\n0.05 * (-12) = -0.6", 2, 0, "purple")
    new = d.box("New value\n7 becomes 6.4", 3, 0, "green")
    for a, b in ((n, df), (df, st), (st, new)):
        d.arrow(a, b)
    d.arrow(new, n, dashed=True, label="repeat every tick")
    d.note("This car starts at x = 7", near=n, side="b")
    d.save(OUT / "diagram-consensus-update.excalidraw")


def modes():
    d = Diagram()
    d.title("The slowest mode sets the pace")
    x = d.box("Gap to the\naverage", 0, 1, "red")
    m2 = d.box("Slowest mode\nlambda2", 1, 1, "yellow")
    ring = d.box("Ring\n0.97 a tick", 2, 0, "yellow")
    comp = d.box("Complete\n0.60 a tick", 2, 1, "green")
    split = d.box("Two groups\nnever shrinks", 2, 2, "red")
    for a, b in ((x, m2), (m2, ring), (m2, comp), (m2, split)):
        d.arrow(a, b)
    d.note("Fast modes die out. The slowest shrinks by 1 - eps * lambda2 a tick. With eps = 0.05, lambda2 is 0.59 on the ring, 8 on the complete graph and 0 on two groups.", d.margin, 0)
    d.save(OUT / "diagram-consensus-modes.excalidraw")


if __name__ == "__main__":
    update()
    modes()
