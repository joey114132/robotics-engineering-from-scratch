# 레슨 05/06 도해: 시각 질의에 보간, 제한 외삽, 거부로 답하는 규칙과 스캔을 찍힌 시각으로 놓는 흐름을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def lookup():
    d = Diagram()
    d.title("One lookup, three possible answers")
    a = d.box("Between two\nsamples", col=0, row=0, color="green")
    b = d.box("Just past\nthe newest", col=0, row=1, color="yellow")
    c = d.box("Too old or\ntoo new", col=0, row=2, color="red")
    ra = d.box("lerp + slerp", col=1, row=0, color="green")
    rb = d.box("Extrapolate if\nunder the limit", col=1, row=1, color="yellow")
    rc = d.box("Raise an\nerror", col=1, row=2, color="red")
    for x, y in ((a, ra), (b, rb), (c, rc)):
        d.arrow(x, y)
    d.note("Each row answers the question: pose at time t?", near=rb, side="b")
    d.save(OUT / "diagram-lookup-rules.excalidraw")


def scan():
    d = Diagram()
    d.title("Which pose places a scan point?")
    n = d.box("Place with the\nnewest pose", col=0, row=0, color="red")
    sm = d.box("Wall looks bent\nwhen rover turns", col=1, row=0, color="red")
    t = d.box("Place with the\npose at its stamp", col=0, row=1, color="green")
    ok = d.box("Wall stays\nstraight", col=1, row=1, color="green")
    d.arrow(n, sm)
    d.arrow(t, ok)
    d.note("Every scan point carries a stamp.", near=n, side="t")
    d.save(OUT / "diagram-scan-stamps.excalidraw")


if __name__ == "__main__":
    lookup()
    scan()
