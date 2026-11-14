# 레슨 06/04 도해: AX = XB 가 생기는 이유와 회전 먼저 이동 나중으로 푸는 순서를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def setup():
    d = Diagram()
    d.title("Why hand-eye calibration is AX = XB")
    a = d.box("Hand moves:\nmotion A (joints)", col=0, row=0, color="blue")
    b = d.box("Camera sees the\nsame move as B", col=0, row=1, color="yellow")
    x = d.box("X: where the camera\nsits on the hand", col=1, row=0.5, color="red")
    e = d.box("A X = X B\nfor every motion", col=2, row=0.5, color="purple")
    for s, t in ((a, x), (b, x), (x, e)):
        d.arrow(s, t)
    d.save(OUT / "diagram-handeye-setup.excalidraw")
    return d.warnings


def solve():
    d = Diagram()
    d.title("Solve rotation first, then translation")
    a = d.box("Rotation axes\nof A and B", col=0, row=0, color="blue")
    b = d.box("Line up the axes\nby SVD: R_X", col=1, row=0, color="purple")
    c = d.box("Stack the\ntranslation rows", col=2, row=0, color="purple")
    e = d.box("t_X by\nleast squares", col=2, row=1, color="green")
    r = d.box("All axes parallel:\nturn and shift free", col=0, row=1, color="red")
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.arrow(a, r, dashed=True)
    d.save(OUT / "diagram-handeye-solve.excalidraw")
    return d.warnings


if __name__ == "__main__":
    print(setup(), solve())
