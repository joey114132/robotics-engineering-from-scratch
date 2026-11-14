# 레슨 00/02 도해: 물리 한 스텝의 순서와 numpy 와 MuJoCo 가 같은 진자를 푸는 두 경로를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def one_step():
    d = Diagram(numbered=True)
    d.title("One physics step")
    a = d.box("Start\n0.5 rad", color="blue")
    b = d.box("Gravity\na = -4.7", color="yellow")
    c = d.box("New speed\nv += a * dt", color="purple")
    e = d.box("Move ball\nby NEW v", color="purple")
    f = d.box("State at\nt + dt", color="green")
    for s, t in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.note("Explicit Euler uses the OLD v here", near=e, side="b")
    d.save(OUT / "diagram-physics-step.excalidraw")


def two_paths():
    d = Diagram()
    d.title("Same pendulum, two solvers")
    p = d.box("Pendulum\nL = 1 m", col=0, row=0.5, color="blue")
    n = d.box("Our numpy\nloop", col=1, row=0, color="purple")
    j = d.box("MuJoCo\nmj_step", col=1, row=1, color="purple")
    r1 = d.box("Period\n2.006 s", col=2, row=0, color="green")
    r2 = d.box("Period\n2.006 s", col=2, row=1, color="green")
    for s, t in ((p, n), (p, j), (n, r1), (j, r2)):
        d.arrow(s, t)
    d.note("Formula 2 pi sqrt(L/g) = 2.006 s", near=r2, side="b")
    d.save(OUT / "diagram-two-solvers.excalidraw")


if __name__ == "__main__":
    one_step()
    two_paths()
