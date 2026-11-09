# 레슨 08/03 도해: 한 번의 scan 이 grid 를 고치는 방식, 자세 오차가 SLAM 문제를 만드는 순환을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def update():
    d = Diagram(cell=(330, 170))
    d.title("What one laser beam tells the grid")
    a = d.box("Beam starts\nat the robot", 0, 0.5, "blue", w=220)
    b = d.box("Cells it crossed\nlog-odds goes down", 1, 0, "green", w=270)
    c = d.box("Cell where it ended\nlog-odds goes up", 1, 1, "red", w=270)
    e = d.box("Cells behind the hit\nnot touched", 2, 0.5, "gray", w=250)
    d.arrow(a, b)
    d.arrow(a, c)
    d.arrow(b, e)
    d.arrow(c, e)
    d.note("Add the numbers beam after beam. Probability = 1 - 1 / (1 + exp(L)).", d.margin, d.margin + 60 + 2 * d.ch + 10, size=20)
    d.save(OUT / "diagram-beam-update.excalidraw")


def slam():
    d = Diagram(cell=(330, 170))
    d.title("Why mapping needs the pose and the pose needs the map")
    p = d.box("Robot pose\n(from odometry)", 0, 0, "yellow", w=240)
    m = d.box("Map built\nfrom scans", 1, 0.5, "purple", w=240)
    e = d.box("Pose error shifts\nevery wall it draws", 2, 0, "red", w=270)
    f = d.box("Smeared, doubled\nwalls", 2, 1, "red", w=270)
    g = d.box("Match scans to the map\nto fix the pose", 1, 2, "green", w=280)
    d.arrow(p, m)
    d.arrow(m, e)
    d.arrow(e, f)
    d.arrow(f, g)
    d.arrow(g, p, route="below")
    d.save(OUT / "diagram-slam-loop.excalidraw")


if __name__ == "__main__":
    update()
    slam()
