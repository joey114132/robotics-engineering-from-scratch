# 레슨 13/04 도해: 래퍼 안의 처리 순서와 관측이 끊겼을 때의 hold/fallback 사다리를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram(numbered=True)
    d.title("The wrapper sits between the policy and the motor")
    o = d.box("Camera frame\n(may be late)", 0, 0, "yellow", step=1)
    g = d.box("Fresh enough?\nelse hold", 1, 0, "purple", step=2)
    p = d.box("Learned\npolicy", 2, 0, "red", step=3)
    c = d.box("Clip and cap\nthe change", 2, 1, "purple", step=4)
    a = d.box("Motor\ncommand", 1, 1, "green", step=5)
    for s, t in ((o, g), (g, p), (p, c), (c, a)):
        d.arrow(s, t)
    d.note("Every change goes to a log", near=c, side="b")
    d.save(OUT / "diagram-wrapper-pipeline.excalidraw")


def ladder():
    d = Diagram()
    d.title("What the wrapper does as the camera frame ages")
    for row, (cond, act, color) in enumerate((
            ("Frame is fresh\n(1 tick old at most)", "Run the policy, then\nclip and rate-limit", "green"),
            ("Frame is late\n(gone up to 10 ticks)", "Hold the last\ncommand", "yellow"),
            ("Frame gone for\nover 10 ticks", "Ramp down to the\nfallback, a stop", "red"))):
        a = d.box(cond, 0, row, "gray")
        b = d.box(act, 1, row, color)
        d.arrow(a, b)
    d.save(OUT / "diagram-wrapper-ladder.excalidraw")


if __name__ == "__main__":
    pipeline()
    ladder()
