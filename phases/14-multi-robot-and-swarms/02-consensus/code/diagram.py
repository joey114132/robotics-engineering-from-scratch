# 레슨 14/02 도해: 로봇 하나의 합의 갱신과, 느린 고유 모드가 속도를 정하는 이유를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def update():
    d = Diagram()
    d.title("One robot, one rule: step toward your neighbours")
    n = d.box("Neighbours' values\nx_j", 0, 0, "blue")
    me = d.box("My value\nx_i", 0, 1, "blue")
    df = d.box("Differences\nx_j - x_i", 1, 0.5, "purple")
    st = d.box("Small step\neps * sum", 2, 0.5, "purple")
    new = d.box("New x_i\ncloser to the group", 3, 0.5, "green")
    for a, b in ((n, df), (me, df), (df, st), (st, new)):
        d.arrow(a, b)
    d.arrow(new, me, route="below", dashed=True, label="repeat every tick", label_dy=-45)
    d.save(OUT / "diagram-consensus-update.excalidraw")


def modes():
    d = Diagram(cell=(330, 170))
    d.title("Disagreement splits into modes, the slowest one rules")
    x = d.box("Disagreement\nx - average", 0, 0.5, "red", w=240)
    m1 = d.box("Fast modes\nlambda large", 1, 0, "gray", w=240)
    m2 = d.box("Slowest mode\nlambda2", 1, 1, "yellow", w=240)
    f = d.box("Gone in\na few steps", 2, 0, "gray", w=230)
    s = d.box("Decays like\n(1 - eps*lambda2)^t", 2, 1, "purple", w=230)
    z = d.box("lambda2 = 0:\nnever agrees", 3, 1, "red", w=230)
    for a, b in ((x, m1), (x, m2), (m1, f), (m2, s), (s, z)):
        d.arrow(a, b)
    d.save(OUT / "diagram-consensus-modes.excalidraw")


if __name__ == "__main__":
    update()
    modes()
