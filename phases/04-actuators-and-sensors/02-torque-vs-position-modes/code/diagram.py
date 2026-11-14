# 레슨 04/02 도해: 토크 모드와 position 모드에서 누가 토크를 쓰는지, 부드러운 관절을 원할 때 고를 수 있는 길을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loops():
    d = Diagram()
    d.title("Who writes the torque?")
    a = d.box("Your code\nsets K, D", col=0, row=0, color="blue")
    b = d.box("Torque command", col=1, row=0, color="purple")
    j1 = d.box("Arm joint\npushed up", col=2, row=0, color="yellow")
    c = d.box("Your code\nsends a target", col=0, row=1, color="blue")
    e = d.box("Drive's PD\nfixed kp_in", col=1, row=1, color="red")
    j2 = d.box("Arm joint\npushed up", col=2, row=1, color="yellow")
    for s, t in ((a, b), (b, j1), (c, e), (e, j2)):
        d.arrow(s, t)
    d.save(OUT / "diagram-mode-loops.excalidraw")


def options():
    d = Diagram()
    d.title("How to get a soft joint")
    q = d.box("You want a joint\nthat gives way", col=0, row=0.5, color="gray")
    t = d.box("Drive takes\ntorque commands", col=1, row=0, color="green")
    p = d.box("Drive takes only\nposition commands", col=1, row=1, color="yellow")
    ti = d.box("Impedance with\nany K, D", col=2, row=0, color="green")
    ad = d.box("Admittance layer\nneeds a torque sensor", col=2, row=1, color="red")
    for s, tt in ((q, t), (q, p), (t, ti), (p, ad)):
        d.arrow(s, tt)
    d.save(OUT / "diagram-mode-options.excalidraw")


if __name__ == "__main__":
    loops()
    options()
