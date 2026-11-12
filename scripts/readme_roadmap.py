# README 학습 경로 도해: 17개 phase 를 여섯 단계로 묶어 뱀 모양 경로로 그린다 (docs/img/roadmap.excalidraw, 렌더는 render_excalidraw.cjs)
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from excal import Diagram  # noqa: E402

d = Diagram(cell=(330, 200))
d.title("17 phases, one path", size=34)
a = d.box("00-01  Start\nsetup and math", 0, 0, "blue", w=280, h=100, size=21)
b = d.box("02-04  The arm\nreach, force, motors", 1, 0, "blue", w=280, h=100, size=21)
c = d.box("05-07  Know\nROS, sensing, filters", 2, 0, "yellow", w=280, h=100, size=21)
e = d.box("08-10  Move\nmobile, planning, legs", 2, 1, "purple", w=280, h=100, size=21)
f = d.box("11-13  Act\ncontact, sim, learning", 1, 1, "purple", w=280, h=100, size=21)
g = d.box("14-16  Ship\nfleets, safety, builds", 0, 1, "green", w=280, h=100, size=21)
for x, y in ((a, b), (b, c), (c, e), (e, f), (f, g)):
    d.arrow(x, y)
d.note("81 lessons. Every one: pictures, a few lines of numpy, a quiz.", d.margin, d.margin + 60 + 2 * d.ch - 40, size=22)
d.save(pathlib.Path(__file__).resolve().parents[1] / "docs" / "img" / "roadmap.excalidraw")
