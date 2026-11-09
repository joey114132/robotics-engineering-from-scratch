# 레슨 02/03 도해: Jacobian 이 속도와 힘을 서로 반대 방향으로 잇는 다리라는 것, 그리고 Jacobian 을 만드는 두 방법을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def bridge():
    d = Diagram(cell=(330, 170))
    d.title("One matrix J, used twice")
    qd = d.box("Joint speeds\nq-dot", 0, 0, "blue", w=210)
    v = d.box("Tip speed\nv = J q-dot", 2, 0, "green", w=220)
    tau = d.box("Joint torques\ntau = J^T F", 0, 1, "green", w=220)
    f = d.box("Tip force\nF", 2, 1, "blue", w=210)
    j = d.box("J(q)\nchanges with pose", 1, 0.5, "purple", w=210)
    d.arrow(qd, j)
    d.arrow(j, v)
    d.arrow(f, j)
    d.arrow(j, tau)
    d.note("Speeds go through J, forces come back through J transposed.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-bridge.excalidraw")


def two_ways():
    d = Diagram(cell=(340, 150))
    d.title("Two ways to build J, one answer")
    a = d.box("Analytic\ndifferentiate FK by hand", 1, 0, "purple", w=260)
    b = d.box("Finite difference\nnudge a joint, watch the tip", 1, 1, "purple", w=290)
    fk = d.box("FK(q)", 0, 0.5, "blue", w=140)
    c = d.box("Compare the\ntwo matrices", 2, 0.5, "yellow", w=210)
    ok = d.box("Agree to 1e-8:\nboth are right", 3, 0, "green", w=220)
    no = d.box("Disagree:\nfind the bug", 3, 1, "red", w=220)
    for s, t in ((fk, a), (fk, b), (a, c), (b, c), (c, ok), (c, no)):
        d.arrow(s, t)
    d.save(OUT / "diagram-two-ways.excalidraw")


if __name__ == "__main__":
    bridge()
    two_ways()
