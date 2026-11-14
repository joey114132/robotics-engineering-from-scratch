# 레슨 14/03 도해: 4대가 서로를 기다리는 교착 고리와, 경로를 한꺼번에 예약해 고리를 없애는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def cycle():
    d = Diagram()
    d.title("Four toy cars wait in a loop")
    a = d.box("Car 0\nholds (0,0)", 0, 0, "red")
    b = d.box("Car 1\nholds (1,0)", 1, 0, "red")
    c = d.box("Car 2\nholds (1,1)", 1, 1, "red")
    e = d.box("Car 3\nholds (0,1)", 0, 1, "red")
    d.arrow(a, b, label="waits for car 1")
    d.arrow(b, c, label="waits for car 2")
    d.arrow(c, e, label="waits for car 3")
    d.arrow(e, a, label="waits for car 0")
    d.note("find_cycle() returns [0, 1, 2, 3]", d.margin, 0)
    d.save(OUT / "diagram-wait-cycle.excalidraw")


def fix():
    d = Diagram()
    d.title("Reservation: take the whole route or wait outside")
    q = d.box("Car wants to\nenter the crossing", 0, 0.5, "blue")
    r = d.box("Is every cell on\nits route free?", 1, 0.5, "purple", shape="diamond")
    y = d.box("Reserve all cells,\ndrive, release\nas it leaves", 2, 0, "green")
    n = d.box("Wait outside,\nholding nothing", 2, 1, "yellow")
    g = d.box("No hold-and-wait,\nso no loop", 3, 0.5, "green")
    d.arrow(q, r)
    d.arrow(r, y, label="yes")
    d.arrow(r, n, label="no")
    d.arrow(y, g)
    d.arrow(n, g)
    d.note("In the clip all four cars finish by tick 7", d.margin, 0)
    d.save(OUT / "diagram-reservation.excalidraw")


if __name__ == "__main__":
    cycle()
    fix()
