# 레슨 05/06 도해: 시각 질의에 보간, 제한 외삽, 거부로 답하는 규칙과 스캔을 찍힌 시각으로 놓는 흐름을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def lookup():
    d = Diagram(cell=(330, 170))
    d.title("One lookup, three possible answers")
    q = d.box("Pose at time t?", 0, 1, "gray", w=220)
    a = d.box("Between two samples", 1, 0, "green", w=250)
    b = d.box("Just past the newest", 1, 1, "yellow", w=250)
    c = d.box("Too old or too new", 1, 2, "red", w=250)
    ra = d.box("lerp + slerp", 2, 0, "green", w=210)
    rb = d.box("Extrapolate if\nunder the limit", 2, 1, "yellow", w=230)
    rc = d.box("Raise an error", 2, 2, "red", w=210)
    for t in (a, b, c):
        d.arrow(q, t)
    for x, y in ((a, ra), (b, rb), (c, rc)):
        d.arrow(x, y)
    d.save(OUT / "diagram-lookup-rules.excalidraw")


def scan():
    d = Diagram(cell=(330, 170))
    d.title("Which pose places a scan point?")
    s = d.box("Scan point\nwith a stamp", 0, 0.5, "blue", w=220)
    n = d.box("Newest pose", 1, 0, "red", w=220)
    t = d.box("Pose at the\nstamp", 1, 1, "green", w=220)
    sm = d.box("Wall looks bent\nwhen robot turns", 2, 0, "red", w=240)
    ok = d.box("Wall stays\nstraight", 2, 1, "green", w=240)
    d.arrow(s, n)
    d.arrow(s, t)
    d.arrow(n, sm)
    d.arrow(t, ok)
    d.save(OUT / "diagram-scan-stamps.excalidraw")


if __name__ == "__main__":
    lookup()
    scan()
