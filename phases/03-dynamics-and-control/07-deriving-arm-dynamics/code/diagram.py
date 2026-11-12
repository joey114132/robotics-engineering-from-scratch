# 레슨 03/07 도해: 에너지에서 출발하는 Lagrange 길과 힘에서 출발하는 Newton-Euler 길이 같은 토크에서 만나는 그림을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def two_roads():
    d = Diagram(cell=(310, 170))
    d.title("Two roads to the same torque")
    a = d.box("Energy road\nwrite T(q, qd)", 0, 0, "blue")
    b = d.box("Differentiate\nd/dt(dT/dqd) - dT/dq", 1, 0, "purple", w=250)
    c = d.box("Force road\nlink accelerations", 0, 2, "blue")
    e = d.box("Walk the chain\nforces, then moments", 1, 2, "purple", w=250)
    t = d.box("Same tau?\nIf not, a bug", 2, 1, "green")
    for s, u in ((a, b), (c, e), (b, t), (e, t)):
        d.arrow(s, u)
    d.save(OUT / "diagram-two-roads.excalidraw")


def parts():
    d = Diagram(cell=(310, 170))
    d.title("Which piece of the energy makes which term")
    t = d.box("T = 1/2 qd' M(q) qd", 0, 1, "blue", w=250)
    m = d.box("M(q): read it off\nwith unit velocities", 1, 0, "green", w=250)
    h = d.box("M changes with q:\nCoriolis, centripetal", 1, 2, "yellow", w=250)
    r = d.box("tau = M qdd + h", 2, 1, "purple", w=230)
    for s, u in ((t, m), (t, h), (m, r), (h, r)):
        d.arrow(s, u)
    d.note("The Coriolis term exists only because M depends on the elbow angle.", d.margin, d.margin + 60 + 2.6 * d.ch, size=20)
    d.save(OUT / "diagram-energy-parts.excalidraw")


if __name__ == "__main__":
    two_roads()
    parts()
