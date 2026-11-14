# 레슨 06/02 도해: 평면 타깃 여러 장에서 내부 파라미터를 푸는 단계와 시점이 부족할 때 실패하는 경우를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def steps():
    d = Diagram()
    d.title("fx, fy, cx, cy from a checkerboard")
    a = d.box("Board corners\n(X, Y) on the board", col=0, row=0, color="blue")
    b = d.box("Corners found\nin each photo (u, v)", col=0, row=1, color="yellow")
    c = d.box("One matrix H\nper view", col=1, row=0.5, color="purple")
    e = d.box("Stack the clues\ninto B", col=2, row=0.5, color="purple")
    f = d.box("Read off\nfx, fy, cx, cy", col=3, row=0.5, color="green")
    for s, t in ((a, c), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.note("No iteration: least squares and one SVD.", near=e, side="b")
    d.save(OUT / "diagram-calib-steps.excalidraw")
    return d.warnings


def views():
    d = Diagram()
    d.title("Which board views can be solved?")
    m = d.box("Board views", col=0, row=0.5, color="gray")
    a = d.box("Only slid: closer,\nfarther, sideways", col=1, row=0, color="red")
    b = d.box("Tilted a new\nway each time", col=1, row=1, color="green")
    ra = d.box("Same clue again:\nrejected", col=2, row=0, color="red")
    rb = d.box("New clue each time:\nK is unique", col=2, row=1, color="green")
    for s, t in ((m, a), (m, b), (a, ra), (b, rb)):
        d.arrow(s, t)
    d.save(OUT / "diagram-calib-views.excalidraw")
    return d.warnings


if __name__ == "__main__":
    print(steps(), views())
