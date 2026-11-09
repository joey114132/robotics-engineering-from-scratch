# 레슨 14/03 도해: 4대가 서로를 기다리는 교착 고리와, 경로를 한꺼번에 예약해 고리를 없애는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def cycle():
    d = Diagram(cell=(330, 190))
    d.title("Wait-for graph: a loop means nobody can move")
    a = d.box("Robot A\nholds (0,0)", 0, 0, "red", w=230)
    b = d.box("Robot B\nholds (1,0)", 1, 0, "red", w=230)
    c = d.box("Robot C\nholds (1,1)", 1, 1, "red", w=230)
    e = d.box("Robot D\nholds (0,1)", 0, 1, "red", w=230)
    d.arrow(a, b, label="wants (1,0)")
    d.arrow(b, c, label="wants (1,1)", label_dx=60)
    d.arrow(c, e, label="wants (0,1)")
    d.arrow(e, a, label="wants (0,0)", label_dx=-60)
    d.save(OUT / "diagram-wait-cycle.excalidraw")


def fix():
    d = Diagram(cell=(330, 170))
    d.title("Reservation: take the whole route or wait outside")
    q = d.box("Robot wants\nto enter", 0, 0.5, "blue", w=230)
    r = d.box("Is every node\non its route free?", 1, 0.5, "purple", w=250, shape="diamond", h=120)
    y = d.box("Reserve all,\ndrive, release\nas it leaves", 2, 0, "green", w=240, h=100)
    n = d.box("Wait outside,\nholding nothing", 2, 1, "yellow", w=240)
    g = d.box("No hold-and-wait\nso no loop", 3, 0.5, "green", w=220)
    for s, t in ((q, r), (r, y), (r, n), (y, g), (n, g)):
        d.arrow(s, t)
    d.save(OUT / "diagram-reservation.excalidraw")


if __name__ == "__main__":
    cycle()
    fix()
