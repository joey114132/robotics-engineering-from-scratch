# 레슨 13/04 도해: 래퍼 안의 처리 순서와 관측이 끊겼을 때의 hold/fallback 사다리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram(cell=(280, 170))
    d.title("The wrapper sits between the policy and the actuator")
    o = d.box("Observation\n(may be late)", 0, 0, "yellow", w=210)
    g = d.box("Fresh enough?\nelse hold or fall back", 1, 0, "purple", w=250, size=18)
    p = d.box("Learned policy\n(varies run to run)", 2, 0, "red", w=220, size=18)
    c = d.box("Clip, then limit\nthe change per tick", 3, 0, "purple", w=230, size=18)
    a = d.box("Actuator", 4, 0, "green", w=170)
    lg = d.box("Intervention log", 2, 1.3, "gray", w=240)
    for s, t in ((o, g), (g, p), (p, c), (c, a), (g, lg), (c, lg)):
        d.arrow(s, t)
    d.save(OUT / "diagram-wrapper-pipeline.excalidraw")


def ladder():
    d = Diagram(cell=(330, 170))
    d.title("What the wrapper does as the observation ages")
    q = d.box("Is the latest\nobservation usable?", 0, 1, "gray", w=240)
    a = d.box("Yes: run the policy,\nthen clip and rate-limit", 1, 0, "green", w=290, size=18)
    b = d.box("No, for a short while:\nhold the last command", 1, 1, "yellow", w=290, size=18)
    c = d.box("No, past the deadline:\nfall back, ramped down", 1, 2, "red", w=290, size=18)
    for t in (a, b, c):
        d.arrow(q, t)
    d.save(OUT / "diagram-wrapper-ladder.excalidraw")


if __name__ == "__main__":
    pipeline()
    ladder()
