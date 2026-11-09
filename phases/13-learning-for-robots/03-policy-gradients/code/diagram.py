# 레슨 13/03 도해: REINFORCE 학습 고리와 기준선이 신호를 바꾸는 방식을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(cell=(310, 170))
    d.title("REINFORCE: try, score, nudge")
    a = d.box("Sample actions\nfrom the Gaussian", 0, 0, "blue", w=230)
    b = d.box("Run episodes,\nadd up rewards", 1, 0, "yellow", w=230)
    c = d.box("Weight each action's\nscore by its return", 2, 0, "purple", w=230)
    e = d.box("Step the\npolicy parameters", 3, 0, "green", w=210)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, route="below", label="repeat", dashed=True)
    d.save(OUT / "diagram-reinforce-loop.excalidraw")


def baseline():
    d = Diagram(cell=(330, 170))
    d.title("What a baseline changes")
    r = d.box("Return of an episode", 0, 0.5, "yellow", w=230)
    raw = d.box("Use it as is:\nevery action pushed up", 1, 0, "red", w=250)
    sub = d.box("Subtract the average\nof the other episodes", 1, 1, "purple", w=250)
    nr = d.box("Noisy step\n(same average)", 2, 0, "red", w=290)
    ns = d.box("Better than average: up\nWorse: down", 2, 1, "green", w=290)
    for s, t in ((r, raw), (r, sub), (raw, nr), (sub, ns)):
        d.arrow(s, t)
    d.save(OUT / "diagram-baseline-effect.excalidraw")


if __name__ == "__main__":
    loop()
    baseline()
