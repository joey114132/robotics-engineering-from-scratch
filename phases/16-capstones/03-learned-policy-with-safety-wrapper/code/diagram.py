# 레슨 16/03 도해: 학습 정책과 안전 wrapper 의 시스템 구성도, spike 와 관측 유실을 wrapper 가 막는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def system():
    d = Diagram(numbered=True, columns=2)
    d.title("A policy inside a safety wrapper")
    demo = d.box("Expert demos\n(PD, 03/04)", 0, 0, "blue", step=1)
    pol = d.box("Policy averages\nclose demos", 1, 0, "purple", step=2)
    wrap = d.box("Wrapper: hold,\nclip, rate limit", 2, 0, "green", step=3)
    arm = d.box("Arm joint\nmoves", 2, 1, "yellow", step=4)
    cam = d.box("Camera picture\nof the joint", 1, 1, "yellow", step=5)
    for a, b in ((demo, pol), (pol, wrap), (wrap, arm), (arm, cam)):
        d.arrow(a, b)
    d.arrow(cam, pol, label="picture", dashed=True)
    d.save(OUT / "diagram-policy-system.excalidraw")
    return d.warnings


def broken():
    d = Diagram(columns=2)
    d.title("Two faults, one wrapper")
    a = d.box("Spike: policy\nasks 40 Nm", 0, 0, "red")
    b = d.box("Clip to 3 Nm,\nrate limit", 1, 0, "green")
    c = d.box("Joint gets\n0.81 Nm", 2, 0, "green")
    e = d.box("Camera lost\nfor 26 steps", 0, 1, "red")
    f = d.box("Picture older\nthan 3 steps: hold", 1, 1, "green")
    g = d.box("Peak 1.01 rad,\nlimit 1.3 rad", 2, 1, "green")
    for x, y in ((a, b), (b, c), (e, f), (f, g)):
        d.arrow(x, y)
    d.save(OUT / "diagram-policy-broken.excalidraw")
    return d.warnings


if __name__ == "__main__":
    print(system(), broken())
