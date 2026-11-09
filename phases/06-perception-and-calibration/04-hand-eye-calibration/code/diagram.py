# 레슨 06/04 도해: AX = XB 가 생기는 이유와 회전 먼저 이동 나중으로 푸는 순서를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def setup():
    d = Diagram()
    d.title("Why hand-eye calibration is AX = XB")
    a = d.box("Gripper moves\nmotion A (from joints)", 0, 0, "blue", w=250)
    b = d.box("Camera sees the\nsame move as B", 0, 1, "yellow", w=250)
    x = d.box("Fixed unknown X\ncamera in gripper frame", 1.3, 0.5, "red", w=270)
    e = d.box("A X = X B\nfor every motion", 2.6, 0.5, "purple", w=240)
    for s, t in ((a, x), (b, x), (x, e)):
        d.arrow(s, t)
    d.note("The camera is bolted to the gripper, so X never changes between motions.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=20)
    d.save(OUT / "diagram-handeye-setup.excalidraw")


def solve():
    d = Diagram(cell=(330, 170))
    d.title("Solve rotation first, then translation")
    a = d.box("Rotation axes\nof A and B", 0, 0.5, "blue", w=220)
    b = d.box("Align the axes\n(SVD): R_X", 1, 0.5, "purple", w=220)
    c = d.box("Stack the\ntranslation rows", 2, 0.5, "purple", w=220)
    e = d.box("t_X by\nleast squares", 3, 0.5, "green", w=200)
    r = d.box("All axes equal:\ntwist about the axis\nis free", 1.5, 1.7, "red", w=260, h=110)
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.arrow(a, r, dashed=True)
    d.note("(R_A - I) t = R_X t_B - t_A, one block of rows per motion", d.margin, d.margin + 60 + 3.3 * d.ch, size=20)
    d.save(OUT / "diagram-handeye-solve.excalidraw")


if __name__ == "__main__":
    setup()
    solve()
