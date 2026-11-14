# 레슨 14/01 도해: 탐욕 배정이 막다른 길에 빠지는 과정과 최적 배정의 아이디어를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def trap():
    d = Diagram(numbered=True)
    d.title("Why greedy strands the last car")
    a = d.box("Each car takes the\nnearest free pad", 0, 0, "blue")
    b = d.box("Car 4 takes pad 5\n(1.1 m away)", 1, 0, "yellow")
    c = d.box("Car 5 is left with\na far pad: 2.2 m", 2, 0, "red")
    g = d.box("Greedy total\n5.3 m", 3, 0, "red")
    for s, t in ((a, b), (b, c), (c, g)):
        d.arrow(s, t)
    d.note("Pad 5 was the only close pad for car 5", d.margin, 0)
    d.save(OUT / "diagram-greedy-trap.excalidraw")


def optimal():
    d = Diagram(numbered=True)
    d.title("Optimal assignment: swap early picks to win overall")
    c = d.box("Distance table\ncars x pads", 0, 0, "blue", step=1)
    p = d.box("Row and column\nprices", 1, 0, "purple", step=2)
    a = d.box("Flip matches on\naugmenting path", 1, 1, "purple", step=3)
    r = d.box("Total is the\nminimum: 3.3 m", 0, 1, "green", step=4)
    for s, t in ((c, p), (p, a), (a, r)):
        d.arrow(s, t)
    d.note("In the clip, cars 3, 4 and 5 trade pads", d.margin, 0)
    d.save(OUT / "diagram-optimal-idea.excalidraw")


if __name__ == "__main__":
    trap()
    optimal()
