# 레슨 03/03 도해: 임피던스 제어의 토크 구성과 K, D 를 고르는 순서를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def structure():
    d = Diagram()
    d.title("Impedance: the joint as a spring and a damper")
    s = d.box("Spring:\nK * error", 0, 0, "blue")
    m = d.box("Damper:\n-D * speed", 0, 1, "blue")
    g = d.box("Gravity\nfeedforward", 0, 2, "blue")
    t = d.box("Motor torque:\nthe three added", 1, 1, "gray")   # one sum box, so every arrow can meet the middle of a side
    f = d.box("Finger pushes\nthe hand: F", 2, 0, "yellow")
    j = d.box("Joint\ninertia J", 2, 1, "purple")
    q = d.box("At rest: it\nsags F / K", 2, 2, "green")
    for a in (s, m, g):
        d.arrow(a, t)
    d.arrow(t, j)
    d.arrow(f, j)
    d.arrow(j, q)
    d.save(OUT / "diagram-impedance-structure.excalidraw")


def recipe():
    d = Diagram(numbered=True)
    d.title("Choosing K and D in four steps")
    a = d.box("Largest push F,\nbudget x_max", 0, 0, "yellow", step=1)
    b = d.box("K = F / x_max", 1, 0, "purple", step=2)
    c = d.box("D = 2*zeta*\nsqrt(K*J)", 1, 1, "purple", step=3)
    e = d.box("Check\ndt*D/J < 1", 0, 1, "green", step=4)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.note("Too big? Lower D or speed up the loop.", near=e, side="b")
    d.note("zeta 0.7 to 1 for contact tasks.", near=c, side="r")
    d.save(OUT / "diagram-impedance-recipe.excalidraw")


if __name__ == "__main__":
    structure()
    recipe()
