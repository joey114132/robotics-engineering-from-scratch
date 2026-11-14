# 레슨 12/03 도해: 기록에서 파라미터를 맞추는 절차와, 느린 궤적 하나가 b 와 c 를 못 가르는 이유를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram(numbered=True)
    d.title("From a recorded run to parameters")
    rec = d.box("Record the arm:\ncommand u, angle q,\nspeed w", 0, 0, "yellow")
    win = d.box("Integrate over\nshort windows", 1, 0, "purple")
    ls = d.box("Least squares\ngives J, b, c", 2, 0, "blue")
    grid = d.box("Grid over Tm,\nkeep the best fit", 2, 1, "green")
    for s, t in ((rec, win), (win, ls), (ls, grid)):
        d.arrow(s, t)
    d.arrow(grid, win, label="Tm changes the columns")
    d.save(OUT / "diagram-id-pipeline.excalidraw")


def collinear():
    d = Diagram()
    d.title("Why one slow run cannot split b from c")
    slow = d.box("Slow run:\nspeed near\n0.28 rad/s", 0, 0, "yellow")
    same = d.box("b*w and c\nstay constant", 1, 0, "red")
    one = d.box("Only the sum is known,\nnot b and c", 2, 0, "red")
    rich = d.box("Rich run:\nspeed rises, falls,\nreverses", 0, 1, "green")
    sep = d.box("b*w changes\nwith speed,\nc does not", 1, 1, "green")
    two = d.box("b and c\nseparate", 2, 1, "green")
    for s, t in ((slow, same), (same, one), (rich, sep), (sep, two)):
        d.arrow(s, t)
    d.save(OUT / "diagram-collinear.excalidraw")


if __name__ == "__main__":
    pipeline()
    collinear()
