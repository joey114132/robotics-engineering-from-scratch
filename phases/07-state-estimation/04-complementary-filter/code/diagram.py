# 레슨 07/04 도해: 상보 필터가 두 센서의 약점을 나눠 맡는 구조와 tau 가 양쪽 오차를 맞바꾸는 모습을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def split():
    d = Diagram()
    d.title("Two sensors, two weaknesses")
    g = d.box("Gyro:\nsmooth, drifts", col=0, row=0, color="yellow")
    hp = d.box("High-pass:\nfast changes", col=1, row=0, color="purple")
    a = d.box("Accel tilt:\nnoisy, no drift", col=0, row=1, color="yellow")
    lp = d.box("Low-pass:\nslow average", col=1, row=1, color="purple")
    s = d.box("Tilt\nestimate", col=2, row=0.5, color="green")
    for x, y in ((g, hp), (a, lp), (hp, s), (lp, s)):
        d.arrow(x, y)
    d.save(OUT / "diagram-comp-split.excalidraw")


def tau():
    d = Diagram()
    d.title("Tuning tau")
    s = d.box("Small tau\n(trust accel)", col=0, row=0, color="red")
    rs = d.box("Board shakes\n(noise)", col=1, row=0, color="red")
    m = d.box("tau in\nbetween", col=0, row=1, color="green")
    rm = d.box("Board nearly\nlevel", col=1, row=1, color="green")
    l = d.box("Large tau\n(trust gyro)", col=0, row=2, color="red")
    rl = d.box("Board leans\n(tau * b)", col=1, row=2, color="red")
    for x, y in ((s, rs), (m, rm), (l, rl)):
        d.arrow(x, y)
    d.save(OUT / "diagram-comp-tau.excalidraw")


if __name__ == "__main__":
    split()
    tau()
