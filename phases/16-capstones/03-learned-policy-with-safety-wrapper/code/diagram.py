# 레슨 16/03 도해: 학습 정책과 안전 wrapper 의 시스템 구성도, 정책 spike 와 관측 유실을 wrapper 가 막는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def system():
    d = Diagram()
    d.title("Learned policy inside a safety wrapper")
    demo = d.box("Expert demos\nPD, lesson 03/04", 0, 0, "blue")
    pol = d.box("Nearest-neighbour\npolicy, new here", 1, 0, "purple")
    wrap = d.box("Safety wrapper\nclip, rate, hold", 2, 0, "green")
    joint = d.box("Simulated joint\nlesson 03/01", 2, 1, "yellow")
    obs = d.box("Observation\n+ age counter", 1, 1, "yellow")
    for a, b in ((demo, pol), (pol, wrap), (wrap, joint), (joint, obs), (obs, pol)):
        d.arrow(a, b)
    d.arrow(obs, wrap, dashed=True, label="age", label_dx=30)
    d.note("The policy is learned. The wrapper is plain code that never learns and always runs.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=18)
    d.save(OUT / "diagram-policy-system.excalidraw")


def broken():
    d = Diagram()
    d.title("Break test: two faults, one wrapper")
    a = d.box("Policy spike\n+40 Nm, one step", 0, 0, "red")
    b = d.box("Clip to the limit,\nlimit the rate", 1, 0, "green")
    c = d.box("Joint barely\nnotices", 2, 0, "green")
    e = d.box("Observation lost\n26 steps", 0, 1, "red")
    f = d.box("Age over 3 steps:\nhold zero torque", 1, 1, "green")
    g = d.box("Joint stays inside\nits limit", 2, 1, "green")
    for x, y in ((a, b), (b, c), (e, f), (f, g)):
        d.arrow(x, y)
    d.note("Without the wrapper the same faults kick the joint and push it past its limit.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=18)
    d.save(OUT / "diagram-policy-broken.excalidraw")


if __name__ == "__main__":
    system()
    broken()
