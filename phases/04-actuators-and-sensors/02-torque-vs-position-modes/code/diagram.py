# 레슨 04/02 도해: 토크 모드와 position 모드의 루프 구조, 그리고 어느 모드에서 무엇이 가능한지를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loops():
    d = Diagram(cell=(300, 170))
    d.title("Who closes the loop?")
    a = d.box("Outer controller\nimpedance K, D", 0, 0, "blue", w=240)
    b = d.box("Torque command", 1, 0, "purple", w=210)
    j1 = d.box("Joint", 2, 0, "yellow", w=170)
    c = d.box("Outer controller\nsends q_des only", 0, 1, "blue", w=240)
    e = d.box("Drive inner PD\nfixed kp, kd", 1, 1, "red", w=210)
    j2 = d.box("Joint", 2, 1, "yellow", w=170)
    for s, t in ((a, b), (b, j1), (c, e), (e, j2)):
        d.arrow(s, t)
    d.note("Top row: torque mode. Bottom row: position mode, the stiffness is not yours.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=20)
    d.save(OUT / "diagram-mode-loops.excalidraw")


def options():
    d = Diagram(cell=(320, 170))
    d.title("What the outer controller can ask for")
    q = d.box("Want a soft,\nyielding joint?", 0, 0.5, "gray", w=230)
    t = d.box("Drive offers torque mode", 1, 0, "green", w=260)
    p = d.box("Position-only drive", 1, 1, "yellow", w=260)
    ti = d.box("Impedance: any K, D", 2, 0, "green", w=250)
    ad = d.box("Add admittance layer\nneeds a torque sensor", 2, 1, "red", w=250)
    for s, tt in ((q, t), (q, p), (t, ti), (p, ad)):
        d.arrow(s, tt)
    d.save(OUT / "diagram-mode-options.excalidraw")


if __name__ == "__main__":
    loops()
    options()
