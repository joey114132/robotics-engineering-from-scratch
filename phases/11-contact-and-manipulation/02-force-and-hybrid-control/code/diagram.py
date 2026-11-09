# 레슨 11/02 도해: 위치 제어가 힘을 놓치는 경로와 하이브리드 위치-힘 제어의 선택 행렬 구조를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def miss():
    d = Diagram()
    d.title("Why position control misses the force")
    a = d.box("Wanted force\nfd = 10 N", 0, 0, "blue")
    b = d.box("Assumed stiffness\nk_est", 0, 1, "gray")
    c = d.box("Command depth\nfd / k_est", 1, 0.5, "purple")
    e = d.box("Real surface\nstiffness ke", 2, 1, "yellow")
    f = d.box("Force = ke * depth\nsoft: miss, stiff: slam", 2, 0, "red", w=250)
    d.arrow(a, c)
    d.arrow(b, c)
    d.arrow(c, f)
    d.arrow(e, f)
    d.note("An integral force loop measures f, so ke drops out.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-position-miss.excalidraw")


def hybrid():
    d = Diagram(cell=(330, 170))
    d.title("Hybrid position-force control")
    s = d.box("Selection matrix\nS = diag(0, 1)", 0, 0.5, "blue", w=240)
    x = d.box("x axis (free)\nposition law", 1, 0, "green", w=240)
    y = d.box("y axis (contact)\nforce law", 1, 1, "red", w=240)
    v = d.box("Tool velocity\n(vx, vy)", 2, 0.5, "purple", w=240)
    d.arrow(s, x, label="1 - S")
    d.arrow(s, y, label="S")
    d.arrow(x, v)
    d.arrow(y, v)
    d.note("Each axis gets exactly one law, never both.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-hybrid-selection.excalidraw")


if __name__ == "__main__":
    miss()
    hybrid()
