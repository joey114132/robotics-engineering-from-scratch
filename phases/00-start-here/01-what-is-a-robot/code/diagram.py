# 레슨 00/01 도해: 로봇의 sense-think-act 되풀이 고리와, 고리 없이 정해진 시간만 달리는 자동차의 결과
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram()
    d.title("A robot repeats three steps")
    s = d.box("Sense\nhow far is the wall?", col=0, row=0, color="blue")
    t = d.box("Think\ngo or stop?", col=1, row=0, color="purple")
    a = d.box("Act\nturn the wheels", col=2, row=0, color="green")
    w = d.box("World\nthe car moves", col=1, row=1, color="yellow")
    d.arrow(s, t)
    d.arrow(t, a)
    d.arrow(a, w)
    d.arrow(w, s, label="new reading")
    d.note("many times a second", near=t, side="t")
    d.save(OUT / "diagram-sense-think-act.excalidraw")


def blind():
    d = Diagram()
    d.title("With and without the loop")
    p = d.box("Plan:\ndrive 4 seconds", col=0, row=0, color="gray")
    c = d.box("Wall is closer\nthan planned", col=1, row=0, color="yellow")
    x = d.box("Crash", col=2, row=0, color="red")
    l = d.box("Loop:\nsense every step", col=0, row=1, color="blue")
    k = d.box("Sees the wall\nand stops", col=1, row=1, color="green")
    d.arrow(p, c)
    d.arrow(c, x)
    d.arrow(l, k)
    d.note("the plan never looks at the wall", near=x, side="b")
    d.save(OUT / "diagram-with-and-without-loop.excalidraw")


if __name__ == "__main__":
    loop()
    blind()
