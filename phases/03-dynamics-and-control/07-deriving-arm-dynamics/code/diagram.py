# 레슨 03/07 도해: 에너지에서 출발하는 Lagrange 길과 힘에서 출발하는 Newton-Euler 길이 같은 토크에서 만나는 그림을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def two_roads():
    d = Diagram()
    d.title("Two roads to the same torque")
    a = d.box("Energy road:\nwrite T(q, qd)", 0, 0, "blue")
    b = d.box("Differentiate:\nd/dt(dT/dqd) - dT/dq", 0, 1, "purple")
    c = d.box("Force road:\nlink accelerations", 1, 0, "blue")
    e = d.box("Walk the chain:\nforces, then moments", 1, 1, "purple")
    t = d.box("Same tau?\nIf not, a bug", 0.5, 2, "green")
    for s, u in ((a, b), (c, e), (b, t), (e, t)):
        d.arrow(s, u)
    d.save(OUT / "diagram-two-roads.excalidraw")


def parts():
    d = Diagram()
    d.title("Which piece of the energy makes which term")
    t = d.box("T = 1/2 qd' M(q) qd", 0.5, 0, "blue")
    m = d.box("M(q): read it off\nwith unit velocities", 0, 1, "green")
    h = d.box("M changes with q:\nCoriolis terms", 1, 1, "yellow")
    r = d.box("tau = M qdd + h", 0.5, 2, "purple")
    for s, u in ((t, m), (t, h), (m, r), (h, r)):
        d.arrow(s, u)
    d.note("No elbow angle in M, no Coriolis term.", near=r, side="b")
    d.save(OUT / "diagram-energy-parts.excalidraw")


if __name__ == "__main__":
    two_roads()
    parts()
