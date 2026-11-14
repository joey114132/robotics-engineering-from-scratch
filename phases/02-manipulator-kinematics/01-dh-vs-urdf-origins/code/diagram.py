# 레슨 02/01 도해: 한 팔의 세 가지 표기와, 규약을 틀렸을 때 조용히 틀리는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def three_ways():
    d = Diagram()
    d.title("One arm, three ways to write it down")
    arm = d.box("Two-link arm\n0.4 m and 0.3 m", col=0, row=1, color="blue")
    t1 = d.box("DH table\n(Craig)", col=1, row=0, color="purple")
    t2 = d.box("DH table\n(standard)", col=1, row=1, color="purple")
    t3 = d.box("URDF origins\nxyz and rpy", col=1, row=2, color="purple")
    fk = d.box("Same hand\nposition (FK)", col=2, row=1, color="green")
    for s, t in ((arm, t1), (arm, t2), (arm, t3), (t1, fk), (t2, fk), (t3, fk)):
        d.arrow(s, t)
    d.save(OUT / "diagram-three-ways.excalidraw")


def silent_wrong():
    d = Diagram()
    d.title("A wrong convention gives no error")
    a = d.box("Table written\nfor Craig", col=0, row=0.5, color="blue")
    b = d.box("Routine written\nfor standard", col=1, row=0.5, color="purple")
    c = d.box("A pose comes out,\nno error", col=2, row=0.5, color="yellow")
    ok = d.box("Zero pose:\nhands match", col=3, row=0, color="green")
    bad = d.box("Elbow bent 0.8 rad:\nhand 0.31 m off", col=3, row=1, color="red")
    for s, t in ((a, b), (b, c), (c, ok), (c, bad)):
        d.arrow(s, t)
    d.save(OUT / "diagram-silent-wrong.excalidraw")


if __name__ == "__main__":
    three_ways()
    silent_wrong()
