# 레슨 13/06 도해: 평균 회귀와 청크 표본기의 갈림, 그리고 청크 겹침 평균을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def split():
    d = Diagram()
    d.title("Two good answers, two ways to use them")
    for row, (first, second, third, color) in enumerate((
            ("Mean\nregression", "Straight at\nthe pillar", "Hits it", "red"),
            ("Sampler:\none chunk", "Commits to\none side", "Clears it", "green"))):
        a = d.box(first, 0, row, "purple")
        b = d.box(second, 1, row, color)
        c = d.box(third, 2, row, color)
        d.arrow(a, b)
        d.arrow(b, c)
    d.note("Half the demos pass above the pillar, half below.", near=a, side="b")
    d.save(OUT / "diagram-average-or-commit.excalidraw")


def overlap():
    d = Diagram(numbered=True)
    d.title("Chunks that overlap and blend")
    a = d.box("Chunk 1: next H\nsteps of one demo", 0, 0, "blue", step=1)
    b = d.box("Chunk 2 starts a few\nsteps later", 1, 0, "blue", step=2)
    c = d.box("Overlap: weighted\naverage of both", 2, 0, "purple", step=3)
    e = d.box("Chunk 2 agrees with\nchunk 1: same side", 2, 1, "green", step=4)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.save(OUT / "diagram-chunk-overlap.excalidraw")


if __name__ == "__main__":
    split()
    overlap()
