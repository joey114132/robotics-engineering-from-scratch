# 레슨 03/03 도해: 임피던스 제어의 토크 구성과 K, D 를 고르는 순서를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def structure():
    d = Diagram()
    d.title("Impedance: the joint as a spring and a damper")
    s = d.box("Spring\nK*(q_des - q)", 0, 0, "blue")
    m = d.box("Damper\n-D * qd", 0, 1, "blue")
    g = d.box("Gravity\nfeedforward", 0, 2, "blue")
    j = d.box("Joint\ninertia J", 1.5, 1, "purple")
    f = d.box("Push from\nthe world, F", 1.5, 2, "yellow")
    q = d.box("Deflection\nF / K at rest", 3, 1, "green")
    for a in (s, m, g):
        d.arrow(a, j)
    d.arrow(f, j)
    d.arrow(j, q)
    d.save(OUT / "diagram-impedance-structure.excalidraw")


def recipe():
    d = Diagram()
    d.title("Choosing K and D in four steps")
    a = d.box("Largest push F\nBudget x_max", 0, 0, "yellow")
    b = d.box("K = F / x_max", 1, 0, "purple")
    c = d.box("D = 2*zeta*\nsqrt(K*J)", 2, 0, "purple")
    e = d.box("Check\ndt*D/J < 1", 3, 0, "green")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, c, label="too big? lower D or speed up the loop", route="below")
    d.note("zeta 0.7 to 1 for contact tasks.", d.margin, d.margin + 60 + 1.6 * d.ch, size=22)
    d.save(OUT / "diagram-impedance-recipe.excalidraw")


if __name__ == "__main__":
    structure()
    recipe()
