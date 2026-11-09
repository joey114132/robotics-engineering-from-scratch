# 레슨 02/01 도해: 한 팔의 세 가지 표기와, 규약을 틀렸을 때 조용히 틀리는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def three_ways():
    d = Diagram(cell=(330, 150))
    d.title("One arm, three ways to write it down")
    arm = d.box("Two-link arm\nL1, L2, two joints", 0, 1, "blue", w=240)
    t1 = d.box("DH table (Craig)\nrow i: a(i-1), alpha(i-1)", 1, 0, "purple", w=270)
    t2 = d.box("DH table (standard)\nrow i: a(i), alpha(i)", 1, 1, "purple", w=270)
    t3 = d.box("URDF origins\nxyz and rpy per joint", 1, 2, "purple", w=270)
    fk = d.box("Same tip pose\nfrom FK", 2, 1, "green", w=220)
    for s, t in ((arm, t1), (arm, t2), (arm, t3), (t1, fk), (t2, fk), (t3, fk)):
        d.arrow(s, t)
    d.save(OUT / "diagram-three-ways.excalidraw")


def silent_wrong():
    d = Diagram(cell=(330, 150))
    d.title("A wrong convention gives no error")
    a = d.box("Table written\nfor Craig", 0, 0.5, "blue", w=230)
    b = d.box("Routine written\nfor standard", 1, 0.5, "purple", w=230)
    c = d.box("A pose comes out\nno exception", 2, 0.5, "yellow", w=230)
    ok = d.box("q = 0: matches", 3, 0, "green", w=200)
    bad = d.box("Any other q:\nwrong pose", 3, 1, "red", w=200)
    for s, t in ((a, b), (b, c), (c, ok), (c, bad)):
        d.arrow(s, t)
    d.note("The zero pose is the check people run, and it passes.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-silent-wrong.excalidraw")


if __name__ == "__main__":
    three_ways()
    silent_wrong()
