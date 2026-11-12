# 레슨 13/06 도해: 평균 회귀와 청크 표본기의 갈림, 그리고 청크 겹침 평균을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def split():
    d = Diagram(cell=(330, 170))
    d.title("Two good answers, two ways to use them")
    s = d.box("Same start, demos\ngo over and under", 0, 0.5, "yellow", w=230)
    m = d.box("Mean regression:\naverage the answers", 1, 0, "purple", w=240)
    c = d.box("Sampler: pick one\ndemo's chunk", 1, 1, "purple", w=240)
    st = d.box("Goes straight", 2, 0, "red", w=190)
    ch = d.box("Commits to a side", 2, 1, "green", w=200)
    hit = d.box("Hits the obstacle", 3, 0, "red", w=190)
    ok = d.box("Clears it", 3, 1, "green", w=170)
    for a, b in ((s, m), (s, c), (m, st), (c, ch), (st, hit), (ch, ok)):
        d.arrow(a, b)
    d.save(OUT / "diagram-average-or-commit.excalidraw")


def overlap():
    d = Diagram(cell=(330, 170))
    d.title("Chunks that overlap and blend")
    a = d.box("Chunk 1: H actions\nfrom one demo", 0, 0, "blue", w=240)
    b = d.box("Chunk 2, a few steps\nlater, must agree\nwith chunk 1", 0, 1, "blue", w=240, h=110)
    c = d.box("Overlap steps:\nweighted average", 1, 0.5, "purple", w=240)
    e = d.box("One way round per\nchunk, smooth actions", 2, 0.5, "green", w=250)
    for x, y in ((a, c), (b, c), (c, e)):
        d.arrow(x, y)
    d.save(OUT / "diagram-chunk-overlap.excalidraw")


if __name__ == "__main__":
    split()
    overlap()
