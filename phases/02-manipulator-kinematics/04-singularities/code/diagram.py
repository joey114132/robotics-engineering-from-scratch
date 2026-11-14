# 레슨 02/04 도해: 팔이 펴질 때 일어나는 연쇄와 damped least squares 가 그 연쇄를 끊는 자리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram(numbered=True)
    d.title("What happens as the arm straightens")
    a = d.box("Elbow angle q2\nshrinks to 0", col=0, row=0, color="yellow")
    b = d.box("det J shrinks\nto 0", col=1, row=0, color="purple")
    c = d.box("One tip direction\nis lost", col=2, row=0, color="red")
    e = d.box("Inverse asks for\nhuge joint speed", col=3, row=0, color="red")
    f = d.box("Drive hits its limit,\ntip leaves the path", col=4, row=0, color="red")
    for s, t in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-chain.excalidraw")


def damping():
    d = Diagram()
    d.title("Damped least squares caps the speed")
    v = d.box("Wanted hand\nvelocity v", col=0, row=0.5, color="blue")
    p = d.box("Plain inverse", col=1, row=0, color="red")
    q = d.box("Damped least\nsquares", col=1, row=1, color="green")
    rp = d.box("Speed grows\nwithout limit", col=2, row=0, color="red")
    rq = d.box("Speed stays under\n|v| / (2 lam)", col=2, row=1, color="green")
    for s, t in ((v, p), (v, q), (p, rp), (q, rq)):
        d.arrow(s, t)
    d.note("price: the tip lags the command", near=rq, side="b")
    d.save(OUT / "diagram-damping.excalidraw")
    print(d.warnings)


if __name__ == "__main__":
    chain()
    damping()
