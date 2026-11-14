# 레슨 08/05 도해: ICP 의 매칭-맞춤 반복 고리와 초기 오차가 점 간격보다 크면 틀린 짝이 생기는 경로를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(numbered=True)
    d.title("ICP: guess the pairs, fit, repeat")
    a = d.box("Two scans\nof one room", -1, 0, "yellow", step=1)
    p = d.box("Pair each dot with\nits nearest dot", 0, 0, "purple", step=2)
    f = d.box("Fit one rigid move\n(SVD, Kabsch)", 1, 0, "purple", step=3)
    mv = d.box("Move the scan,\nmeasure the error", 1, 1, "blue", step=4)
    q = d.box("Error still\nfalling?", 0, 1, "gray", step=5)
    done = d.box("Done", 0, 2, "green", step=6)
    d.arrow(a, p)
    d.arrow(p, f)
    d.arrow(f, mv)
    d.arrow(mv, q)
    d.arrow(q, p, label="yes")
    d.arrow(q, done, label="no")
    d.save(OUT / "diagram-icp-loop.excalidraw")


def failure():
    d = Diagram(numbered=True)
    d.title("Why a big start ends wrong")
    a = d.box("Scan starts far\noff: 2.6 rad", 0, 0, "red", step=1)
    b = d.box("Nearest dot is not\nthe true twin", 1, 0, "red", step=2)
    c = d.box("Fit is best for\nthe wrong pairs", 1, 1, "purple", step=3)
    e = d.box("Stuck: error\nstays 0.54 m", 0, 1, "yellow", step=4)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.note("cure: start from odometry", near=a, side="t")
    d.save(OUT / "diagram-icp-failure.excalidraw")


if __name__ == "__main__":
    loop()
    failure()
