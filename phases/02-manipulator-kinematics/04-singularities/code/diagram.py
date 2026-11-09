# 레슨 02/04 도해: 팔이 펴질 때 일어나는 연쇄와 damped least squares 가 그 연쇄를 끊는 자리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram(cell=(330, 150))
    d.title("What happens as the arm straightens")
    a = d.box("Elbow angle q2\nshrinks to 0", 0, 0.5, "yellow", w=220)
    b = d.box("det J = L1 L2 sin q2\nshrinks to 0", 1, 0.5, "purple", w=250)
    c = d.box("One tip direction\nis lost (radial)", 2, 0, "red", w=230)
    e = d.box("Inverse asks for\nhuge joint speed", 2, 1, "red", w=230)
    f = d.box("Drive saturates,\ntip leaves the path", 3, 1, "red", w=230)
    for s, t in ((a, b), (b, c), (b, e), (e, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-chain.excalidraw")


def damping():
    d = Diagram(cell=(400, 150))
    d.title("Damped least squares caps the speed")
    v = d.box("Wanted tip\nvelocity v", 0, 0.5, "blue", w=200)
    p = d.box("Plain inverse\nqd = J^-1 v", 1, 0, "red", w=240)
    q = d.box("Damped least squares\nadds lam^2 I to the inverse", 1, 1, "green", w=340)
    rp = d.box("Speed grows\nwithout limit", 2, 0, "red", w=220)
    rq = d.box("Speed stays under\n|v| / (2 lam)", 2, 1, "green", w=240)
    for s, t in ((v, p), (v, q), (p, rp), (q, rq)):
        d.arrow(s, t)
    d.note("The price: near the singularity the tip lags the command.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-damping.excalidraw")


if __name__ == "__main__":
    chain()
    damping()
