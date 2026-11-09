# 레슨 07/03 도해: 적분 횟수가 drift 의 차수를 정하는 흐름과, gyro bias 가 중력을 통해 위치로 새는 사슬을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def orders():
    d = Diagram()
    d.title("Each integral raises the drift order")
    g = d.box("Gyro rate\n+ small bias b", 0, 0, "yellow", w=210)
    gi = d.box("Integrate\nonce", 1, 0, "purple", w=190)
    ge = d.box("Angle error\n= b t  (linear)", 2, 0, "red", w=230)
    a = d.box("Accel\n+ small bias a", 0, 1, "yellow", w=210)
    ai = d.box("Integrate\ntwice", 1, 1, "purple", w=190)
    ae = d.box("Position error\n= a t^2 / 2", 2, 1, "red", w=230)
    for s, t in ((g, gi), (gi, ge), (a, ai), (ai, ae)):
        d.arrow(s, t)
    d.save(OUT / "diagram-drift-orders.excalidraw")


def leak():
    d = Diagram(cell=(310, 170))
    d.title("Gyro bias leaks into position through gravity")
    b = d.box("Gyro bias b", 0, 0, "yellow", w=200)
    t = d.box("Tilt estimate\nwrong by b t", 1, 0, "purple", w=220)
    g = d.box("Gravity seen\nas g sin(b t)", 2, 0, "purple", w=220)
    p = d.box("Position error\n~ g b t^3 / 6", 3, 0, "red", w=240)
    for s, e in ((b, t), (t, g), (g, p)):
        d.arrow(s, e)
    d.note("Over a long run, t^3 overtakes t^2.", d.margin, d.margin + 60 + d.ch - 20, size=22)
    d.save(OUT / "diagram-gravity-leak.excalidraw")


if __name__ == "__main__":
    orders()
    leak()
