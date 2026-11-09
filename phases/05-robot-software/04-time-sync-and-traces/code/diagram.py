# 레슨 05/04 도해: 요청/응답 네 개의 시각으로 offset 을 구하는 흐름과, trace 의 pre/post 쌍으로 첫 불일치를 찾는 흐름을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def exchange():
    d = Diagram(cell=(300, 170))
    d.title("Offset from four timestamps")
    a = d.box("Client sends\nt0 (client clock)", 0, 0, "blue", w=220)
    b = d.box("Server gets\nt1 (server clock)", 1, 0, "yellow", w=220)
    c = d.box("Server replies\nt2 (server clock)", 2, 0, "yellow", w=220)
    e = d.box("Client gets\nt3 (client clock)", 3, 0, "blue", w=220)
    o = d.box("offset = ((t1-t0) + (t2-t3)) / 2", 1, 1.3, "purple", w=480)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, o, route="below")
    d.save(OUT / "diagram-offset-exchange.excalidraw")


def trace():
    d = Diagram(cell=(300, 170))
    d.title("Find the first record that disagrees")
    i = d.box("Intent\nstep, target", 0, 0.5, "blue", w=200)
    t = d.box("Trace line\npre and post", 1, 0.5, "yellow", w=210)
    r = d.box("Reader walks\nsteps in order", 2, 0.5, "purple", w=220)
    n = d.box("not executed", 3, 0, "red", w=210)
    m = d.box("no motion", 3, 1, "red", w=210)
    w = d.box("wrong motion", 3, 2, "red", w=210)
    d.arrow(i, t)
    d.arrow(t, r)
    for x in (n, m, w):
        d.arrow(r, x)
    d.save(OUT / "diagram-trace-reader.excalidraw")


if __name__ == "__main__":
    exchange()
    trace()
