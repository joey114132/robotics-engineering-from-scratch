# 레슨 08/06 도해: pose graph 의 변수와 스프링 구조, 루프 폐쇄가 지도를 되감는 파이프라인을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def graph():
    d = Diagram()
    d.title("A pose graph: poses are unknowns, edges are springs")
    p0 = d.box("Pose 0\n(held fixed)", 0, 0, "gray", w=190)
    p1 = d.box("Pose 1", 1, 0, "blue", w=160)
    p2 = d.box("Pose 2 ...", 2, 0, "blue", w=170)
    pn = d.box("Pose 20\n(same place)", 3, 0, "blue", w=190)
    d.arrow(p0, p1, label="odometry")
    d.arrow(p1, p2, label="odometry")
    d.arrow(p2, pn, label="odometry")
    d.arrow(pn, p0, route="below", label="loop closure: we are back here")
    d.note("Solving = find poses that stretch every spring as little as possible.", d.margin, d.margin + 60 + d.ch + 60, size=22)
    d.save(OUT / "diagram-posegraph-springs.excalidraw")


def pipeline():
    d = Diagram(cell=(330, 170))
    d.title("How a late correction repairs old poses")
    a = d.box("Odometry drifts\nthe loop is open", 0, 0, "red", w=230)
    b = d.box("Scan match sees\nthe start again", 1, 0, "yellow", w=240)
    c = d.box("Add one\nclosure edge", 2, 0, "purple", w=210)
    e = d.box("Gauss-Newton\nre-solves all poses", 3, 0, "purple", w=240)
    g = d.box("Loop snaps shut,\nerror spread out", 3, 1, "green", w=240)
    for s, t in ((a, b), (b, c), (c, e), (e, g)):
        d.arrow(s, t)
    d.save(OUT / "diagram-posegraph-pipeline.excalidraw")


if __name__ == "__main__":
    graph()
    pipeline()
