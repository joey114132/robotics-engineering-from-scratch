# 레슨 03/09 도해: Lyapunov 검사의 논리와 단일 시뮬레이션이 놓치는 반례를 표본 검사가 찾는 모습을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def logic():
    d = Diagram()
    d.title("The Lyapunov test in three boxes")
    a = d.box("V >= 0, and 0 only\nat the goal", 0, 0.5, "blue", w=250)
    b = d.box("dV/dt <= 0\nat every state", 1, 0.5, "purple", w=250)
    c = d.box("V never rises,\nstate stays close", 2, 0.5, "green", w=250)
    d.arrow(a, b)
    d.arrow(b, c)
    d.note("V is a made-up energy. You choose it, then check the sign of its slope.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=21)
    d.save(OUT / "diagram-lyapunov-logic.excalidraw")


def sweep():
    d = Diagram(cell=(330, 170))
    d.title("One run can look fine. A sweep cannot hide.")
    s = d.box("Negative damping\n(unstable)", 0, 1, "red", w=230)
    r = d.box("Run once from rest", 1, 0, "yellow", w=250)
    w = d.box("Sample many states,\ncheck dV/dt", 1, 2, "purple", w=250)
    ro = d.box("Stays at 0.\nLooks stable", 2, 0, "yellow", w=230)
    wo = d.box("dV/dt > 0 found.\nCounterexample", 2, 2, "red", w=230)
    for x, y in ((s, r), (s, w), (r, ro), (w, wo)):
        d.arrow(x, y)
    d.save(OUT / "diagram-lyapunov-sweep.excalidraw")


if __name__ == "__main__":
    logic()
    sweep()
