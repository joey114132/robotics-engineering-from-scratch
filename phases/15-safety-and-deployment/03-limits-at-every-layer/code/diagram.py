# 레슨 15/03 도해: 계층별 한계가 안쪽으로 포개지는 정상 구조와, 한계가 어긋났을 때 조용히 이기는 쪽을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def nested():
    d = Diagram(cell=(300, 170))
    d.title("Healthy: each layer is looser than the one before")
    p = d.box("Planner\nvel 1.0", 0, 0, "blue", w=210)
    c = d.box("Controller\nvel 1.5", 1, 0, "purple", w=210)
    r = d.box("Drive\nvel 2.0", 2, 0, "gray", w=210)
    j = d.box("Joint", 3, 0, "yellow", w=160)
    for s, t in ((p, c), (c, r), (r, j)):
        d.arrow(s, t)
    d.note("The planner clamps first and the later layers are safety nets that never fire in normal use.", d.margin, d.margin + 60 + d.ch - 10, size=20)
    d.save(OUT / "diagram-limits-nested.excalidraw")


def silent():
    d = Diagram(cell=(300, 170))
    d.title("Mismatch: the tightest layer wins and nobody says so")
    p = d.box("Planner asks\nvel 3.0", 0, 0, "blue", w=210)
    c = d.box("Controller allows\nvel 3.0", 1, 0, "purple", w=230)
    r = d.box("Drive allows\nvel 1.5", 2, 0, "red", w=210)
    j = d.box("Joint moves\nat 1.5", 3, 0, "yellow", w=190)
    for s, t in ((p, c), (c, r), (r, j)):
        d.arrow(s, t)
    chk = d.box("Startup check\ncompares every pair", 1, 1.4, "green", w=260)
    msg = d.box("Report each mismatch\nbefore the first move", 2, 1.4, "green", w=260)
    d.arrow(chk, msg)
    d.arrow(c, chk, dashed=True)
    d.save(OUT / "diagram-limits-silent.excalidraw")


if __name__ == "__main__":
    nested()
    silent()
