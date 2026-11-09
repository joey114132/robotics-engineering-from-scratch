# 레슨 06/02 도해: 평면 타깃 여러 장에서 내부 파라미터를 푸는 단계와 시점이 부족할 때 실패하는 경우를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def steps():
    d = Diagram()
    d.title("Intrinsics from a flat target in four linear steps")
    a = d.box("Known grid points\n(X, Y) on a plane", 0, 0, "blue")
    b = d.box("Detected pixels\n(u, v), several views", 0, 1, "yellow")
    c = d.box("Per view\nhomography H (DLT)", 1.2, 0.5, "purple", w=250)
    e = d.box("Stack constraints\non B = K^-T K^-1", 2.4, 0.5, "purple", w=250)
    f = d.box("Read off\nfx, fy, cx, cy", 3.6, 0.5, "green", w=230)
    for s, t in ((a, c), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.note("Every step is a least-squares or an SVD. No iteration.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-calib-steps.excalidraw")


def views():
    d = Diagram(cell=(330, 170))
    d.title("Which views make the problem solvable?")
    m = d.box("Views of the\nflat target", 0, 0.5, "gray", w=230)
    a = d.box("Same orientation,\nonly shifted", 1, 0, "red", w=250)
    b = d.box("Several different\ntilts", 1, 1, "green", w=250)
    ra = d.box("Constraints repeat:\nrejected as degenerate", 2, 0, "red", w=250, h=100)
    rb = d.box("Constraints differ:\nintrinsics are unique", 2, 1, "green", w=250, h=100)
    for s, t in ((m, a), (m, b), (a, ra), (b, rb)):
        d.arrow(s, t)
    d.save(OUT / "diagram-calib-views.excalidraw")


if __name__ == "__main__":
    steps()
    views()
