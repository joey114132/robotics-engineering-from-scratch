# 레슨 07/03 도해: 적분 횟수가 drift 의 차수를 정하는 흐름과, gyro bias 가 중력을 통해 위치로 새는 사슬을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def orders():
    d = Diagram()
    d.title("Each integral raises the drift order")
    g = d.box("Gyro bias\n(robot still)", col=0, row=0, color="yellow")
    gi = d.box("Add up\nonce", col=1, row=0, color="purple")
    ge = d.box("Angle error\nb t", col=2, row=0, color="red")
    a = d.box("Accel bias\n(robot still)", col=0, row=1, color="yellow")
    ai = d.box("Add up\ntwice", col=1, row=1, color="purple")
    ae = d.box("Position\na t^2 / 2", col=2, row=1, color="red")
    for s, t_ in ((g, gi), (gi, ge), (a, ai), (ai, ae)):
        d.arrow(s, t_)
    d.save(OUT / "diagram-drift-orders.excalidraw")


def leak():
    d = Diagram(numbered=True)
    d.title("Gyro bias leaks into position through gravity")
    b = d.box("Gyro bias b\nrobot still", col=0, row=0, color="yellow")
    t = d.box("Tilt guess\noff by b t", col=1, row=0, color="purple")
    g = d.box("Fake push:\ng sin(b t)", col=2, row=0, color="purple")
    p = d.box("Position\ng b t^3 / 6", col=2, row=1, color="red")
    for s, e in ((b, t), (t, g), (g, p)):
        d.arrow(s, e)
    d.save(OUT / "diagram-gravity-leak.excalidraw")


if __name__ == "__main__":
    orders()
    leak()
