# 레슨 00/06 도해: 시간 스텝 한 번의 순서와, 큰 스텝과 작은 스텝이 실제 운동을 따라가는 정도를 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def one_step():
    d = Diagram(numbered=True)
    d.title("One time step")
    a = d.box("Old speed\nand position", color="blue")
    b = d.box("Speed changes\nby push x step", color="purple")
    c = d.box("Position moves\nby speed x step", color="purple")
    e = d.box("New speed\nand position", color="green")
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.note("Repeat this many times a second", near=e, side="b")
    d.save(OUT / "diagram-one-step.excalidraw")


def big_small():
    d = Diagram()
    d.title("Big steps and small steps")
    real = d.box("Real motion\nsmooth", col=0, row=0.5, color="yellow")
    big = d.box("Big steps\nfew jumps", col=1, row=0, color="red")
    small = d.box("Small steps\nmany hops", col=1, row=1, color="green")
    far = d.box("Drifts away\nfrom real", col=2, row=0, color="red")
    close = d.box("Stays close\nto real", col=2, row=1, color="green")
    for s, t in ((real, big), (real, small), (big, far), (small, close)):
        d.arrow(s, t)
    d.note("Small steps cost more work", near=close, side="b")
    d.save(OUT / "diagram-big-small.excalidraw")


if __name__ == "__main__":
    one_step()
    big_small()
