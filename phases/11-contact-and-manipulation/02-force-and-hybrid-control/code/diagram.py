# 레슨 11/02 도해: 위치 제어가 스펀지 강성 때문에 힘을 놓치는 경로와, 미끄러지는 축과 누르는 축에 서로 다른 법칙을 주는 하이브리드 제어를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def miss():
    d = Diagram()
    d.title("Why position control misses the force")
    a = d.box("Want 10 N\non the sponge", 0, 0, "blue")
    b = d.box("Assume sponge\n5000 N/m", 0, 1, "gray")
    c = d.box("Push 2 mm deep\n(10 / 5000)", 1, 0.5, "purple")
    e = d.box("Real sponge\n1000 N/m", 1, 1.5, "yellow")
    f = d.box("Real force\n1.6 N, not 10 N", 2, 0.5, "red")
    d.arrow(a, c)
    d.arrow(b, c)
    d.arrow(c, f)
    d.arrow(e, f)
    d.note("A force loop measures f, so the stiffness drops out.", near=f, side="b")
    d.save(OUT / "diagram-position-miss.excalidraw")


def hybrid():
    d = Diagram()
    d.title("Hybrid position-force control")
    s = d.box("Selection:\nS = diag(0,1)", 0, 0.5, "blue")
    x = d.box("x: slide along\nposition law", 1, 0, "green")
    y = d.box("y: press down\nforce law", 1, 1, "red")
    v = d.box("Tool velocity\n(vx, vy)", 2, 0.5, "purple")
    d.arrow(s, x, label="1 - S")
    d.arrow(s, y, label="S")
    d.arrow(x, v)
    d.arrow(y, v)
    d.note("Each axis gets exactly one law, never both.", near=v, side="b")
    d.save(OUT / "diagram-hybrid-selection.excalidraw")


if __name__ == "__main__":
    miss()
    hybrid()
