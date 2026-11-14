# 레슨 01/04 도해: 카메라, 손(tool), 컵이 달린 frame 트리와 공통 조상 base 를 거치는 조회 경로를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def tree():
    d = Diagram()
    d.title("A transform tree: one parent per frame")
    w = d.box("world", 0, 0, "gray")
    b = d.box("base\narm foot", 1, 0, "blue")
    c = d.box("cam\ncamera", 2, 0, "purple")
    t = d.box("tool\nhand", 1, 1, "purple")
    cup = d.box("cup", 2, 1, "yellow")
    for s, e in ((w, b), (b, c), (b, t), (c, cup)):
        d.arrow(s, e)
    d.save(OUT / "diagram-tf-tree.excalidraw")


def lookup():
    d = Diagram(numbered=True)
    d.title("lookup(tool, cup) = T_tool_cup")
    a = d.box("Climb from cup\ncup, cam, base", 0, 0, "blue", step=1)
    c = d.box("Meet at\nbase", 1, 0, "yellow", step=3)
    b = d.box("Climb from tool\ntool, base", 2, 0, "blue", step=2)
    r = d.box("inv(T_base_tool) @\nT_base_cup", 1, 1, "green", step=4)
    d.arrow(a, c)
    d.arrow(b, c)
    d.arrow(c, r)
    d.save(OUT / "diagram-tf-lookup.excalidraw")


if __name__ == "__main__":
    tree()
    lookup()
