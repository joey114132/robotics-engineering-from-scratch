# 레슨 05/02 도해: 단일 스레드 executor 가 느린 callback 때문에 timer 를 굶기는 흐름과 callback group 의 효과를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def starve():
    d = Diagram()
    d.title("One thread, one slow callback")
    r = d.box("Heartbeat timer\nready every 10 ms", col=0, row=0, color="blue")
    e = d.box("One thread\none job at a time", col=1, row=0, color="purple")
    w = d.box("Heartbeat waits\nup to 59 ms", col=2, row=0, color="red")
    s = d.box("Slow callback\nruns 60 ms", col=1, row=1, color="yellow")
    d.arrow(r, e)
    d.arrow(e, w)
    d.arrow(s, e)
    d.save(OUT / "diagram-executor-starve.excalidraw")


def groups():
    d = Diagram()
    d.title("Two threads help only with two groups")
    a = d.box("Timer and slow\nsame group", col=0, row=0, color="red")
    c = d.box("2 threads, but\none at a time", col=1, row=0, color="red")
    f = d.box("Timer still\nwaits", col=2, row=0, color="red")
    b = d.box("Timer and slow\nown groups", col=0, row=1, color="green")
    e = d.box("2 threads run\nin parallel", col=1, row=1, color="green")
    g = d.box("Timer on\ntime", col=2, row=1, color="green")
    for s, t in ((a, c), (c, f), (b, e), (e, g)):
        d.arrow(s, t)
    d.save(OUT / "diagram-callback-groups.excalidraw")


if __name__ == "__main__":
    starve()
    groups()
