# 레슨 16/02 도해: 내비게이션 시스템 구성도와 같은 바퀴 오차에서 보정이 없을 때와 있을 때가 갈리는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def system():
    d = Diagram(numbered=True, columns=2)
    d.title("Plan with a map, steer by a guess")
    grid = d.box("Room grid,\nwalls inflated", 0, 0, "blue", step=1)
    astar = d.box("A* route,\n77 waypoints", 1, 0, "purple", step=2)
    short = d.box("Shortcuts,\n6 waypoints", 2, 0, "purple", step=3)
    pursuit = d.box("Pure pursuit\nsteers", 2, 1, "purple", step=4)
    rover = d.box("Rover drives,\nwheels read off", 1, 1, "yellow", step=5)
    guess = d.box("Guess of where\nthe rover is", 0, 1, "gray", step=6)
    for a, b in ((grid, astar), (astar, short), (short, pursuit), (pursuit, rover), (rover, guess)):
        d.arrow(a, b)
    d.arrow(guess, pursuit, label="steer by it", dashed=True)
    d.note("posts reset it", near=guess, side="b")
    d.save(OUT / "diagram-nav-system.excalidraw")
    return d.warnings


def broken():
    d = Diagram(columns=2)
    d.title("Same wheel error, with and without a fix")
    a = d.box("Guess drifts\n4.7 m off", 0, 0, "red")
    b = d.box("Rover steers\nby the guess", 1, 0, "red")
    c = d.box("Rover hits\nthe wall", 2, 0, "red")
    e = d.box("Two posts seen\neach second", 0, 1, "green")
    f = d.box("Guess stays\nwithin 0.11 m", 1, 1, "green")
    g = d.box("Rover reaches\nthe goal", 2, 1, "green")
    for x, y in ((a, b), (b, c), (e, f), (f, g)):
        d.arrow(x, y)
    d.note("no fix", near=a, side="t")
    d.note("fix every second", near=e, side="t")
    d.save(OUT / "diagram-nav-broken.excalidraw")
    return d.warnings


if __name__ == "__main__":
    print(system(), broken())
