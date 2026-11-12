# 레슨 01/05 도해: 세 고리가 한 줄로 서는 gimbal lock 과, 매끄러운 움직임이 180도 점프로 읽히는 과정을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def rings():
    d = Diagram()
    d.title("Three rings, one hole")
    y = d.box("Yaw ring\n(turns first, outer)", 0, 0, "blue", w=240)
    p = d.box("Pitch ring\n(middle)", 1, 0, "purple", w=240)
    r = d.box("Roll ring\n(inner)", 2, 0, "green", w=240)
    t = d.box("Tool", 3, 0, "gray", w=160)
    for a, b in ((y, p), (p, r), (r, t)):
        d.arrow(a, b)
    bad = d.box("Pitch = 90 deg:\nroll axis = yaw axis", 1, 1.4, "red", w=260)
    res = d.box("Two rings turn the\nsame way: 1 DOF lost", 2.4, 1.4, "yellow", w=260)
    d.arrow(p, bad)
    d.arrow(bad, res)
    d.save(OUT / "diagram-gimbal-rings.excalidraw")


def jump():
    d = Diagram(cell=(330, 170))
    d.title("A smooth turn that reads as a sensor bug")
    a = d.box("Real motion:\npitch 89 to 91 deg", 0, 0.5, "yellow", w=250)
    b = d.box("Reads\nroll 0, yaw 0", 1, 0, "blue", w=220)
    c = d.box("Reads\nroll 180, yaw 180", 1, 1, "blue", w=220)
    e = d.box("Angles jump\n180 deg: 'bug'", 2, 0.5, "red", w=230)
    f = d.box("Keep R or a quaternion;\nEuler only to display", 3, 0.5, "green", w=270)
    for s, t in ((a, b), (a, c), (b, e), (c, e), (e, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-angle-jump.excalidraw")


if __name__ == "__main__":
    rings()
    jump()
