# 레슨 13/03 도해: REINFORCE 학습 고리와 기준선이 신호를 바꾸는 방식을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(numbered=True)
    d.title("REINFORCE: try, score, nudge")
    a = d.box("Car steers with\nsome random noise", 0, 0, "blue", step=1)
    b = d.box("Each try ends with\na total reward", 1, 0, "yellow", step=2)
    c = d.box("Weight each move\nby that return", 1, 1, "purple", step=3)
    e = d.box("Nudge the\nsteering rule", 0, 1, "green", step=4)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, a, label="repeat", dashed=True)
    d.save(OUT / "diagram-reinforce-loop.excalidraw")


def baseline():
    d = Diagram()
    d.title("What a baseline changes")
    for row, (first, second, color) in enumerate((
            ("Use the return\nas it is", "Every move is\npushed up", "red"),
            ("Subtract the\nothers' average", "Better up,\nworse down", "green"))):
        a = d.box("Try returns\n35.9, 34.9, 27.6, 27.3" if row == 0 else "Same returns", 0, row, "yellow")
        b = d.box(first, 1, row, "purple" if row else "gray")
        c = d.box(second, 2, row, color)
        d.arrow(a, b)
        d.arrow(b, c)
    d.save(OUT / "diagram-baseline-effect.excalidraw")


if __name__ == "__main__":
    loop()
    baseline()
