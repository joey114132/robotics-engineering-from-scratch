# 레슨 01/03 도해: q 와 -q 의 이중 덮개, 그리고 부호 보정 slerp 의 판단 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def cover():
    d = Diagram(cell=(330, 170))
    d.title("Two quaternions, one rotation")
    q = d.box("q = (w, x, y, z)", 0, 0, "blue", w=240)
    nq = d.box("-q = (-w, -x, -y, -z)", 0, 1, "blue", w=240)
    R = d.box("Same rotation\nmatrix R", 1, 0.5, "green", w=240)
    d.arrow(q, R)
    d.arrow(nq, R)
    d.note("Opposite points on a sphere in 4D, one pose in 3D.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=20)
    d.save(OUT / "diagram-double-cover.excalidraw")


def flow():
    d = Diagram(cell=(330, 170))
    d.title("Slerp with the sign fix")
    a = d.box("Start q0\ntarget q1", 0, 0.5, "blue", w=200)
    c = d.box("dot(q0, q1)\nnegative?", 1, 0.5, "yellow", w=220, shape="diamond", h=110)
    y = d.box("Yes: negate q1\nshort arc", 2, 0, "green", w=240)
    n = d.box("No: keep q1\nshort arc", 2, 1, "green", w=240)
    bad = d.box("Skipped the check:\nlong arc, wrist spins", 1, 1.9, "red", w=300)
    d.arrow(a, c)
    d.arrow(c, y, label="yes")
    d.arrow(c, n, label="no")
    d.arrow(c, bad, dashed=True)
    d.save(OUT / "diagram-slerp-sign-fix.excalidraw")


if __name__ == "__main__":
    cover()
    flow()
