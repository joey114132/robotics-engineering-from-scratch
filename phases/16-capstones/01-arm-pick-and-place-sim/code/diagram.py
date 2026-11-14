# 레슨 16/01 도해: pick-and-place 시스템 구성도와 중력 feedforward 를 뺐을 때 miss 가 생기는 연쇄를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def system():
    d = Diagram(numbered=True, columns=2)
    d.title("Pick and place: one chain, four ideas")
    stops = d.box("Ball at A,\nmarker at B", 0, 0, "blue", step=1)
    ik = d.box("Joint angles\n(IK, 02/02)", 1, 0, "purple", step=2)
    path = d.box("Smooth path\n(quintic, 09/01)", 2, 0, "purple", step=3)
    pd = d.box("PD + gravity ff\n(03/02)", 2, 1, "purple", step=4)
    arm = d.box("Bench arm\nmoves", 1, 1, "yellow", step=5)
    check = d.box("Tip within\n5 mm of B?", 0, 1, "green", step=6)
    for a, b in ((stops, ik), (ik, path), (path, pd), (pd, arm), (arm, check)):
        d.arrow(a, b)
    d.arrow(arm, pd, label="angles", dashed=True)
    d.save(OUT / "diagram-pick-place-system.excalidraw")
    return d.warnings


def broken():
    d = Diagram(numbered=True)
    d.title("Break test: take the feedforward away")
    a = d.box("Feedforward\nremoved", 0, 0, "gray", step=1)
    b = d.box("Shoulder holds\n6.11 Nm alone", 1, 0, "red", step=2)
    c = d.box("Spring sinks\n6.11/150 = 0.04 rad", 2, 0, "purple", step=3)
    e = d.box("Tip ends 20 mm\noff the marker", 2, 1, "red", step=4)
    f = d.box("Place check\nFAILS", 1, 1, "red", step=5)
    for s, t in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.note("with ff, no sag", near=a, side="b")
    d.save(OUT / "diagram-pick-place-broken.excalidraw")
    return d.warnings


if __name__ == "__main__":
    print(system(), broken())
