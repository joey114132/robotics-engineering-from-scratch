# 레슨 01/04 도해: 이름 붙은 frame 트리와 공통 조상을 거치는 조회 경로를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def tree():
    d = Diagram(cell=(300, 150))
    d.title("A transform tree: one parent per frame")
    w = d.box("world", 0, 0.5, "gray", w=180)
    b = d.box("base", 1, 0.5, "blue", w=180)
    c = d.box("cam", 2, 0, "purple", w=180)
    t = d.box("tool", 2, 1, "purple", w=180)
    cup = d.box("cup", 3, 0, "yellow", w=180)
    for s, e in ((w, b), (b, c), (b, t), (c, cup)):
        d.arrow(s, e)
    d.note("Each arrow stores T_parent_child.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=20)
    d.save(OUT / "diagram-tf-tree.excalidraw")


def lookup():
    d = Diagram(cell=(330, 170))
    d.title("lookup(tool, cup) = T_tool_cup")
    a = d.box("Up from cup\ncup, cam, base", 0, 0, "blue", w=240)
    b = d.box("Up from tool\ntool, base", 0, 1, "blue", w=240)
    c = d.box("Common ancestor\nbase", 1, 0.5, "yellow", w=220)
    r = d.box("inv(T_base_tool) @\nT_base_cup", 2, 0.5, "green", w=260)
    for s, e in ((a, c), (b, c), (c, r)):
        d.arrow(s, e)
    d.save(OUT / "diagram-tf-lookup.excalidraw")


if __name__ == "__main__":
    tree()
    lookup()
