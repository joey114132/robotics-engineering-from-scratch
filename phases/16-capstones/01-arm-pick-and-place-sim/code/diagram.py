# 레슨 16/01 도해: pick-and-place 시스템 구성도와 중력 feedforward 를 뺐을 때의 연쇄를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def system():
    d = Diagram()
    d.title("Pick and place: which lesson each part comes from")
    t = d.box("Block at A,\ngoal at B", 0, 0, "blue")
    ik = d.box("IK waypoints\nlesson 02/02", 1, 0, "purple")
    tr = d.box("Quintic path\nlesson 09/01", 2, 0, "purple")
    pd = d.box("PD + gravity ff\nlesson 03/02", 2, 1, "purple")
    arm = d.box("Simulated arm\nnew here", 1, 1, "yellow")
    ck = d.box("Tip error at B\nbelow 5 mm?", 0, 1, "green")
    for s, e in ((t, ik), (ik, tr), (tr, pd), (pd, arm), (arm, ck)):
        d.arrow(s, e)
    d.note("The arm's angles flow back into the PD loop every millisecond.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=20)
    d.save(OUT / "diagram-pick-place-system.excalidraw")


def broken():
    d = Diagram(cell=(300, 170))
    d.title("Break test: remove the gravity feedforward")
    a = d.box("Gravity ff\nremoved", 0, 0, "gray")
    b = d.box("Residual =\nfull gravity torque", 1, 0, "red")
    c = d.box("Spring sag\n= residual / kp", 2, 0, "purple")
    e = d.box("Tip lands\n2 cm off", 2, 1, "red")
    f = d.box("Place check\nFAILS", 1, 1, "red")
    for s, t in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.note("Same sag as lesson 03/02, now with a task attached.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=20)
    d.save(OUT / "diagram-pick-place-broken.excalidraw")


if __name__ == "__main__":
    system()
    broken()
