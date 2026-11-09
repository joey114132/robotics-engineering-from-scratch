# 레슨 05/02 도해: 단일 스레드 executor 가 느린 callback 때문에 timer 를 굶기는 흐름과 callback group 의 효과를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def starve():
    d = Diagram(cell=(310, 170))
    d.title("One thread, one slow callback")
    r = d.box("Timer ready\nevery 10 ms", 0, 0, "blue", w=230)
    s = d.box("Slow callback\nstarts, 60 ms", 0, 1, "yellow", w=230)
    e = d.box("Executor thread\nruns one at a time", 1, 0.5, "purple", w=240)
    w = d.box("Timer waits\nup to 59 ms", 2, 0.5, "red", w=230)
    d.arrow(r, e)
    d.arrow(s, e)
    d.arrow(e, w)
    d.save(OUT / "diagram-executor-starve.excalidraw")


def groups():
    d = Diagram(cell=(320, 170))
    d.title("Two threads help only with two groups")
    a = d.box("Timer and slow\nsame group", 0, 0, "red", w=240)
    b = d.box("Timer and slow\nown groups", 0, 1, "green", w=240)
    c = d.box("2 threads\nstill one at a time", 1, 0, "red", w=240)
    e = d.box("2 threads\nrun in parallel", 1, 1, "green", w=240)
    f = d.box("Timer still waits", 2, 0, "red", w=220)
    g = d.box("Timer on time", 2, 1, "green", w=220)
    for s, t in ((a, c), (b, e), (c, f), (e, g)):
        d.arrow(s, t)
    d.save(OUT / "diagram-callback-groups.excalidraw")


if __name__ == "__main__":
    starve()
    groups()
