# 레슨 05/04 도해: 요청/응답 네 개의 시각으로 offset 을 구하는 흐름과, trace 의 pre/post 쌍으로 첫 불일치를 찾는 흐름을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def exchange():
    d = Diagram(numbered=True)
    d.title("Offset from four timestamps")
    a = d.box("Client sends\nt0, client clock", col=0, row=0, color="blue", step=1)
    b = d.box("Server gets\nt1, server clock", col=1, row=0, color="yellow", step=2)
    c = d.box("Server replies\nt2, server clock", col=2, row=0, color="yellow", step=3)
    e = d.box("Client gets\nt3, client clock", col=2, row=1, color="blue", step=4)
    o = d.box("offset =\n((t1-t0)+(t2-t3))/2", col=1, row=1, color="purple", step=5)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, o)
    d.save(OUT / "diagram-offset-exchange.excalidraw")


def trace():
    d = Diagram(numbered=True)
    d.title("Find the first record that disagrees")
    i = d.box("Intent:\nstep and target", col=0, row=0, color="blue", step=1)
    t = d.box("Trace line:\npre and post", col=1, row=0, color="yellow", step=2)
    r = d.box("Reader checks\nsteps in order", col=2, row=0, color="purple", step=3)
    n = d.box("First mismatch:\nstop here", col=2, row=1, color="red", step=4)
    d.arrow(i, t)
    d.arrow(t, r)
    d.arrow(r, n)
    d.note("not executed, no motion or wrong motion", near=n, side="l")
    d.save(OUT / "diagram-trace-reader.excalidraw")


if __name__ == "__main__":
    exchange()
    trace()
