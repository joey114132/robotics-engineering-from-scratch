# 레슨 13/01 도해: 시연에서 정책까지의 흐름과 두 모방 정책의 차이를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram(numbered=True)
    d.title("Imitation: copy what the expert did")
    a = d.box("Expert drives the\nrover round the pillar", 0, 0, "blue")
    b = d.box("Record pairs:\nspot and steering", 1, 0, "yellow")
    c = d.box("Fit a function:\nspot to steering", 2, 0, "purple")
    e = d.box("Rover drives\nby itself", 3, 0, "green")
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.note("No reward, no model of the world: only examples.", near=e, side="b")
    d.save(OUT / "diagram-imitation-pipeline.excalidraw")


def fits():
    d = Diagram()
    d.title("Same demonstrations, two fits")
    for row, (name, fit, result, color) in enumerate((
            ("Demos pass the\npillar left or right", "Least squares:\none straight rule", "Averages: drives\ninto the pillar", "red"),
            ("Same demos", "3 nearest spots:\ncopy their actions", "Copies one side:\nswerves round", "green"))):
        a = d.box(name, 0, row, "yellow")
        b = d.box(fit, 1, row, "gray")
        r = d.box(result, 2, row, color)
        d.arrow(a, b)
        d.arrow(b, r)
    d.save(OUT / "diagram-imitation-fits.excalidraw")


if __name__ == "__main__":
    pipeline()
    fits()
