# 레슨 02/03 도해: Jacobian 이 속도와 힘을 서로 반대 방향으로 잇는 다리라는 것, 그리고 Jacobian 을 만드는 두 방법을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def bridge():
    d = Diagram()
    d.title("One matrix J, used twice")
    qd = d.box("Speeds\nq-dot", col=0, row=0, color="blue")
    j1 = d.box("Times J", col=1, row=0, color="purple")
    v = d.box("Tip speed\nv = J q-dot", col=2, row=0, color="green")
    f = d.box("Force F\n(2 kg block)", col=0, row=1, color="blue")
    j2 = d.box("Times J^T", col=1, row=1, color="purple")
    tau = d.box("Torques\ntau = J^T F", col=2, row=1, color="green")
    d.arrow(qd, j1)
    d.arrow(j1, v)
    d.arrow(f, j2)
    d.arrow(j2, tau)
    d.save(OUT / "diagram-bridge.excalidraw")


def two_ways():
    d = Diagram()
    d.title("Two ways to build J, one answer")
    a = d.box("Build J twice:\nby formula, by nudging", col=0, row=0.5, color="purple")
    c = d.box("Same J?", col=1, row=0.5, color="yellow", shape="diamond")
    ok = d.box("Yes: both\nare right", col=2, row=0, color="green")
    no = d.box("No: find\nthe bug", col=2, row=1, color="red")
    d.arrow(a, c)
    d.arrow(c, ok, label="yes")
    d.arrow(c, no, label="no")
    d.save(OUT / "diagram-two-ways.excalidraw")
    print(d.warnings)


if __name__ == "__main__":
    bridge()
    two_ways()
