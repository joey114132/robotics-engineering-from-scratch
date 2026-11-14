# 레슨 03/09 도해: Lyapunov 검사의 논리와 단일 시뮬레이션이 놓치는 반례를 표본 검사가 찾는 모습을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def logic():
    d = Diagram(numbered=True)
    d.title("The Lyapunov test in three boxes")
    a = d.box("V >= 0, and 0 only\nat the goal", 0, 0, "blue")
    b = d.box("dV/dt <= 0\nat every state", 0, 1, "purple")
    c = d.box("V never rises,\nstate stays close", 0, 2, "green")
    d.arrow(a, b)
    d.arrow(b, c)
    d.note("V is a made-up energy. You choose it, then check the sign of its slope.", near=c, side="b")
    d.save(OUT / "diagram-lyapunov-logic.excalidraw")


def sweep():
    d = Diagram()
    d.title("One run can look fine. A sweep cannot hide.")
    s = d.box("Negative damping\n(unstable)", 0.5, 0, "red")
    r = d.box("Run once\nfrom rest", 0, 1, "yellow")
    w = d.box("Sample many states,\ncheck dV/dt", 1, 1, "purple")
    ro = d.box("Stays at 0.\nLooks stable", 0, 2, "yellow")
    wo = d.box("dV/dt > 0 found.\nCounterexample", 1, 2, "red")
    for x, y in ((s, r), (s, w), (r, ro), (w, wo)):
        d.arrow(x, y)
    d.save(OUT / "diagram-lyapunov-sweep.excalidraw")


if __name__ == "__main__":
    logic()
    sweep()
