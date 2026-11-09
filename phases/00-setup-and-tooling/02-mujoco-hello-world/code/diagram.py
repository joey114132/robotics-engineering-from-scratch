# 레슨 00/02 도해: 물리 한 스텝의 순서와 numpy 와 MuJoCo 가 같은 진자를 푸는 두 경로를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def one_step():
    d = Diagram(cell=(280, 170))
    d.title("One physics step")
    a = d.box("State\ntheta, omega", 0, 0.5, "blue", w=190)
    b = d.box("Force to\nacceleration", 1, 0.5, "purple", w=210)
    c = d.box("omega += a * dt", 2, 0, "purple", w=210)
    e = d.box("theta += omega * dt\n(NEW omega)", 2, 1, "purple", w=230)
    f = d.box("State at\nt + dt", 3, 0.5, "green", w=190)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.note("Repeat every dt. Order matters: velocity first, then position.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=20)
    d.save(OUT / "diagram-physics-step.excalidraw")


def two_paths():
    d = Diagram(cell=(310, 170))
    d.title("Same pendulum, two solvers")
    p = d.box("Pendulum\nL, g, theta0", 0, 0.5, "blue", w=210)
    n = d.box("numpy loop\nsemi-implicit Euler", 1, 0, "purple", w=250)
    j = d.box("MuJoCo\nMJCF string + mj_step", 1, 1, "purple", w=250)
    r1 = d.box("Period\n2.006 s", 2, 0, "green", w=190)
    r2 = d.box("Period\n2.006 s", 2, 1, "green", w=190)
    for s, t in ((p, n), (p, j), (n, r1), (j, r2)):
        d.arrow(s, t)
    d.note("Both agree with 2 pi sqrt(L/g) for a small swing.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=20)
    d.save(OUT / "diagram-two-solvers.excalidraw")


if __name__ == "__main__":
    one_step()
    two_paths()
