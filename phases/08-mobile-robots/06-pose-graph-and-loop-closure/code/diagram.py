# 레슨 08/06 도해: pose graph 의 변수와 스프링 구조, 루프 폐쇄가 지도를 되감는 파이프라인을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def graph():
    d = Diagram()
    d.title("Poses are unknowns, edges are springs")
    p0 = d.box("Pose 0\nstart, held fixed", 0, 0, "gray")
    p1 = d.box("Pose 1\nafter 1 m", 1, 0, "blue")
    p2 = d.box("Pose 2 ...\nafter 2 m", 1, 1, "blue")
    pn = d.box("Pose 20\nsame place as 0", 0, 1, "blue")
    d.arrow(p0, p1, label="odometry")
    d.arrow(p1, p2, label="odometry")
    d.arrow(p2, pn, label="odometry")
    d.arrow(pn, p0, label="loop closure")
    d.note("solve: least total stretch", near=pn, side="b")
    d.save(OUT / "diagram-posegraph-springs.excalidraw")


def pipeline():
    d = Diagram(numbered=True)
    d.title("How a late correction repairs old poses")
    a = d.box("Odometry drifts,\nthe loop is open", 0, 0, "red", step=1)
    b = d.box("Scan match sees\nthe start again", 1, 0, "yellow", step=2)
    c = d.box("Add one\nclosure edge", 1, 1, "purple", step=3)
    e = d.box("Gauss-Newton\nre-solves all poses", 0, 1, "purple", step=4)
    g = d.box("Loop snaps shut,\nerror spread out", 0, 2, "green", step=5)
    for s_, t in ((a, b), (b, c), (c, e), (e, g)):
        d.arrow(s_, t)
    d.save(OUT / "diagram-posegraph-pipeline.excalidraw")


if __name__ == "__main__":
    graph()
    pipeline()
