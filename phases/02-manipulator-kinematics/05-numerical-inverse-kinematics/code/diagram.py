# 레슨 02/05 도해: 반복 IK 한 걸음의 순환과 여러 seed 에서 여러 해로 가는 재시작 흐름을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(cell=(360, 170))
    d.title("One step of numerical IK")
    a = d.box("Error\ne = target - fk(q)", 0, 0, "red", w=240)
    b = d.box("Damped solve\ndq = J^T (J J^T + lam^2 I)^-1 e", 1, 0, "purple", w=330, size=18, dx=-10)
    c = d.box("Clamp to\njoint limits", 2, 0, "yellow", w=220, dx=20)
    e = d.box("Forward kinematics\nof the new q", 1.5, 1.3, "blue", w=260)
    f = d.box("|e| < tol:\nreturn q", 3, 1.3, "green", w=220)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, label="repeat", route="below")
    d.arrow(e, f)
    d.save(OUT / "diagram-ik-loop.excalidraw")


def restarts():
    d = Diagram(cell=(330, 170))
    d.title("Many seeds, several answers")
    s = d.box("Random seeds\ninside the limits", 0, 0.5, "gray", w=240)
    a = d.box("Elbow up\nsolution", 1, 0, "blue", w=220)
    b = d.box("Elbow down\nsolution", 1, 1, "blue", w=220)
    x = d.box("Stuck at a limit\nconverged = False", 1, 2, "red", w=250)
    p = d.box("Pick by cost:\nclosest to now", 2, 0.5, "green", w=240)
    for t in (a, b, x):
        d.arrow(s, t)
    d.arrow(a, p)
    d.arrow(b, p)
    d.save(OUT / "diagram-ik-restarts.excalidraw")


if __name__ == "__main__":
    loop()
    restarts()
