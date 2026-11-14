# 레슨 08/03 도해: 한 번의 scan 이 grid 를 고치는 방식, 자세 오차가 SLAM 문제를 만드는 순환을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def update():
    d = Diagram()
    d.title("What one laser beam tells the grid")
    a = d.box("Beam leaves\nthe rover", 0, 1, "blue")
    b = d.box("Cells it crossed:\nL goes down by 0.4", 1, 0, "green")
    c = d.box("Cell where it ended:\nL goes up by 0.85", 1, 1, "red")
    e = d.box("Cells behind the hit:\nnot touched", 1, 2, "gray")
    for t in (b, c, e):
        d.arrow(a, t)
    d.save(OUT / "diagram-beam-update.excalidraw")


def slam():
    d = Diagram(numbered=True)
    d.title("Mapping needs pose, pose needs map")
    p = d.box("Pose from odometry\n(a little off)", 0, 0, "yellow", step=1)
    m = d.box("Draw the scan\ninto the map", 1, 0, "purple", step=2)
    g = d.box("Match the next scan\nto the map so far", 1, 1, "green", step=3)
    f = d.box("Corrected pose", 0, 1, "green", step=4)
    d.arrow(p, m)
    d.arrow(m, g)
    d.arrow(g, f)
    d.arrow(f, p)
    d.note("wrong pose = smeared walls", near=p, side="t")
    d.save(OUT / "diagram-slam-loop.excalidraw")


if __name__ == "__main__":
    update()
    slam()
