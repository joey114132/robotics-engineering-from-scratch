# 레슨 09/03 도해: 얇은 기둥을 말뚝이 건너뛰는 과정과 half-step 패딩 규칙을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def tunnel():
    d = Diagram()
    d.title("How the car drives through a post")
    a = d.box("Post is 0.5 wide\n(2r)", 0, 0, "red")
    b = d.box("Pegs 1.0 apart,\nwider than the post", 0, 1, "yellow")
    c = d.box("Pegs land before\nand after the post", 0, 2, "purple")
    e = d.box("All pegs say free,\ncar hits the post", 0, 3, "red")
    f = d.box("Exact test:\nclosest point", 1, 1, "green")
    g = d.box("Sees the hit", 1, 2, "green")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(f, g)
    d.note("both tests use the same segment and post", near=f, side="t")
    d.save(OUT / "diagram-tunnel.excalidraw")


def rule():
    d = Diagram()
    d.title("Choosing the peg spacing s")
    s = d.box("Pegs every s", 0, 0, "blue")
    a = d.box("s at most 2r:\ncentre hits seen", 0, 1, "green")
    b = d.box("A graze can\nslip through", 0, 2, "red")
    p = d.box("Pad the post\nby s / 2", 1, 1, "purple")
    r = d.box("Never misses,\nmay over-warn", 1, 2, "green")
    for x, y in ((s, a), (s, p), (a, b), (p, r)):
        d.arrow(x, y)
    d.save(OUT / "diagram-step-rule.excalidraw")


if __name__ == "__main__":
    tunnel()
    rule()
