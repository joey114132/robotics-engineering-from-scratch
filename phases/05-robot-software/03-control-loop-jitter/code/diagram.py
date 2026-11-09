# 레슨 05/03 도해: 고정 주기 loop 한 바퀴의 구성과 평균이 최악을 가리는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def anatomy():
    d = Diagram(cell=(300, 170))
    d.title("One turn of a fixed-rate loop")
    a = d.box("Sleep until\ni x period", 0, 0, "gray", w=210)
    b = d.box("Wake late\nby a random delay", 1, 0, "yellow", w=220)
    c = d.box("Do the work\n0.2 ms", 2, 0, "blue", w=200)
    e = d.box("Done before the\nnext deadline?", 3, 0, "purple", shape="diamond", w=230, h=120)
    m = d.box("No: deadline\nmissed", 3, 1.3, "red", w=210)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, m, label="late")
    d.save(OUT / "diagram-loop-anatomy.excalidraw")


def hide():
    d = Diagram(cell=(320, 170))
    d.title("Why the average hides the problem")
    s = d.box("5000 loop periods", 0, 0.5, "gray", w=230)
    m = d.box("Mean jitter\n0 us: looks fine", 1, 0, "green", w=240)
    w = d.box("Worst jitter\n1.5 ms: one spike", 1, 1, "red", w=240)
    r = d.box("The motor feels\nthe worst one", 2, 0.5, "yellow", w=230)
    d.arrow(s, m)
    d.arrow(s, w)
    d.arrow(m, r, dashed=True)
    d.arrow(w, r)
    d.save(OUT / "diagram-average-hides.excalidraw")


if __name__ == "__main__":
    anatomy()
    hide()
