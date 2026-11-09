# 레슨 07/04 도해: 상보 필터가 두 센서의 약점을 나눠 맡는 구조와 tau 가 양쪽 오차를 맞바꾸는 모습을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def split():
    d = Diagram()
    d.title("Two sensors, two weaknesses")
    g = d.box("Gyro\nsmooth, but drifts", 0, 0, "yellow", w=230)
    a = d.box("Accel tilt\nnoisy, never drifts", 0, 1, "yellow", w=230)
    hp = d.box("High-pass\nkeep fast changes", 1, 0, "purple", w=230)
    lp = d.box("Low-pass\nkeep slow average", 1, 1, "purple", w=230)
    s = d.box("Tilt estimate", 2, 0.5, "green", w=210)
    for x, y in ((g, hp), (a, lp), (hp, s), (lp, s)):
        d.arrow(x, y)
    d.save(OUT / "diagram-comp-split.excalidraw")


def tau():
    d = Diagram(cell=(330, 170))
    d.title("Tuning tau trades one error for the other")
    s = d.box("Small tau", 0, 0, "red", w=210)
    l = d.box("Large tau", 0, 2, "red", w=210)
    m = d.box("tau in between", 0, 1, "green", w=210)
    rs = d.box("Trusts accel:\nnoisy output", 1, 0, "red", w=250)
    rl = d.box("Trusts gyro:\nbias error tau * b", 1, 2, "red", w=250)
    rm = d.box("Both errors\nsmall", 1, 1, "green", w=250)
    for x, y in ((s, rs), (l, rl), (m, rm)):
        d.arrow(x, y)
    d.save(OUT / "diagram-comp-tau.excalidraw")


if __name__ == "__main__":
    split()
    tau()
