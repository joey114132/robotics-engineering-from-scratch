# 레슨 05/03 도해: 고정 주기 loop 한 바퀴의 구성과 평균이 최악을 가리는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def anatomy():
    d = Diagram(numbered=True)
    d.title("One turn of a fixed-rate loop")
    a = d.box("Sleep until\ni x T", col=0, row=0, color="gray", step=1)
    b = d.box("Wake a\nlittle late", col=1, row=0, color="yellow", step=2)
    c = d.box("Work\n0.2 ms", col=2, row=0, color="blue", step=3)
    e = d.box("Done before\nnext deadline?", col=2, row=1, color="purple", shape="diamond", step=4)
    m = d.box("Deadline\nmissed", col=1, row=1, color="red", step=5)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, m, label="no")
    d.note("If yes, sleep until the next i x T.", near=a, side="b")
    d.save(OUT / "diagram-loop-anatomy.excalidraw")


def hide():
    d = Diagram()
    d.title("Why the average hides the problem")
    m = d.box("Mean jitter\n0 us", col=0, row=0, color="green")
    ok = d.box("Looks\nhealthy", col=1, row=0, color="green")
    w = d.box("Worst cycle\n1.5 ms late", col=0, row=1, color="red")
    r = d.box("Motor\ntwitches", col=1, row=1, color="red")
    d.arrow(m, ok)
    d.arrow(w, r)
    d.note("Same 5000 cycles, two very different answers.", near=r, side="r")
    d.save(OUT / "diagram-average-hides.excalidraw")


if __name__ == "__main__":
    anatomy()
    hide()
