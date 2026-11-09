# 레슨 12/03 도해: 기록에서 파라미터를 맞추는 절차와, 느린 궤적 하나가 b 와 c 를 못 가르는 이유를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram(cell=(300, 170))
    d.title("From a recorded run to parameters")
    rec = d.box("Record command u,\nangle q, speed w", 0, 0.5, "yellow", w=230)
    win = d.box("Integrate over\nshort windows", 1, 0.5, "purple", w=210)
    ls = d.box("Least squares:\nJ, b, c", 2, 0.5, "blue", w=200)
    grid = d.box("Grid over Tm,\nkeep best residual", 3, 0.5, "green", w=230)
    for s, t in ((rec, win), (win, ls), (ls, grid)):
        d.arrow(s, t)
    d.arrow(grid, ls, route="below", label="Tm changes the columns")
    d.save(OUT / "diagram-id-pipeline.excalidraw")


def collinear():
    d = Diagram(cell=(330, 170))
    d.title("Why one slow run cannot split b from c")
    slow = d.box("One slow run:\nspeed is nearly constant", 0, 0, "yellow", w=290)
    same = d.box("b*w and c*sign(w)\nare both constant", 1, 0, "red", w=270)
    one = d.box("Only b*w + c is known,\nnot b and c", 2, 0, "red", w=270)
    rich = d.box("Rich run:\nspeed and sign change", 0, 1.3, "green", w=290)
    sep = d.box("b*w grows with speed,\nc*sign(w) does not", 1, 1.3, "green", w=270)
    two = d.box("b and c\nseparate", 2, 1.3, "green", w=270)
    for s, t in ((slow, same), (same, one), (rich, sep), (sep, two)):
        d.arrow(s, t)
    d.save(OUT / "diagram-collinear.excalidraw")


if __name__ == "__main__":
    pipeline()
    collinear()
