# 레슨 08/05 도해: ICP 의 매칭-맞춤 반복 고리와 초기 오차가 점 간격보다 크면 틀린 짝이 생기는 경로를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("ICP: guess the pairs, fit, repeat")
    a = d.box("Two scans\nof one room", 0, 1, "yellow", w=200)
    m = d.box("Pair each point\nwith its nearest", 1, 0, "purple", w=240)
    f = d.box("Fit one rigid move\n(SVD, Kabsch)", 2, 0, "purple", w=240)
    mv = d.box("Move the scan,\nmeasure the error", 3, 1, "blue", w=240)
    done = d.box("Error stops\nfalling: done", 3, 0, "green", w=220)
    d.arrow(a, m)
    d.arrow(m, f)
    d.arrow(f, mv)
    d.arrow(mv, done)
    d.arrow(mv, a, route="below", label="not done: pair again")
    d.save(OUT / "diagram-icp-loop.excalidraw")


def failure():
    d = Diagram(cell=(330, 170))
    d.title("Why a big start offset ends in a wrong answer")
    a = d.box("Start offset is\nbigger than the\npoint spacing", 0, 0, "red", w=230)
    b = d.box("Nearest point is\nnot the true twin", 1, 0, "red", w=240)
    c = d.box("Fit is right for\nthe wrong pairs", 2, 0, "purple", w=240)
    e = d.box("Stuck in a\nlocal minimum", 3, 0, "yellow", w=220)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.note("A better start (odometry) or a bigger search is the cure.", d.margin, d.margin + 60 + d.ch - 20, size=22)
    d.save(OUT / "diagram-icp-failure.excalidraw")


if __name__ == "__main__":
    loop()
    failure()
