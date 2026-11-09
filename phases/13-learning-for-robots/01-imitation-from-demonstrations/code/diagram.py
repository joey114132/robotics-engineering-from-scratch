# 레슨 13/01 도해: 시연에서 정책까지의 흐름과 두 모방 정책의 차이를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram()
    d.title("Imitation: copy what the expert did")
    a = d.box("Expert drives\naround the obstacle", 0, 0.5, "blue")
    b = d.box("Record pairs\n(observation, action)", 1, 0.5, "yellow", w=250)
    c = d.box("Fit a function\nobservation to action", 2, 0.5, "purple")
    e = d.box("Policy drives\nby itself", 3, 0.5, "green")
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.note("No reward, no model of the world: only examples.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-imitation-pipeline.excalidraw")


def fits():
    d = Diagram(cell=(330, 170))
    d.title("Same demonstrations, two fits")
    data = d.box("Demonstrations\n(position, velocity)", 0, 0.5, "yellow", w=240)
    lin = d.box("Least squares\none straight rule", 1, 0, "gray", w=250)
    knn = d.box("k nearest neighbours\ncopy the closest demos", 1, 1, "gray", w=250)
    rl = d.box("Smooth average:\nplows into the obstacle", 2, 0, "red", w=250)
    rk = d.box("Local copy:\nswerves like the expert", 2, 1, "green", w=250)
    for s, t in ((data, lin), (data, knn), (lin, rl), (knn, rk)):
        d.arrow(s, t)
    d.save(OUT / "diagram-imitation-fits.excalidraw")


if __name__ == "__main__":
    pipeline()
    fits()
