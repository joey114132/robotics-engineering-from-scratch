# 레슨 02/05 도해: 반복 IK 한 걸음의 순환과 여러 seed 에서 여러 해로 가는 재시작 흐름을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def loop():
    d = Diagram(numbered=True)
    d.title("One step of numerical IK")
    a = d.box("Error: target\nminus fk(q)", col=0, row=0, color="red", step=1)
    b = d.box("Damped solve\nfor a small dq", col=1, row=0, color="purple", step=2)
    c = d.box("Clamp to\njoint limits", col=2, row=0, color="yellow", step=3)
    e = d.box("Forward kinematics\nof the new q", col=2, row=1, color="blue", step=4)
    f = d.box("Error tiny:\nreturn q", col=1, row=1, color="green", step=5)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f, label="done")
    d.arrow(e, a, label="repeat")
    d.save(OUT / "diagram-ik-loop.excalidraw")


def restarts():
    d = Diagram()
    d.title("Many seeds, several answers")
    s = d.box("20 random\nstart poses", col=0, row=0, color="gray")
    r = d.box("Run solve_ik\nfrom each seed", col=0, row=1, color="purple")
    ok = d.box("17 converge:\nelbow up or down", col=0, row=2, color="blue")
    p = d.box("Pick the one\nclosest to now", col=0, row=3, color="green")
    for a, b in ((s, r), (r, ok), (ok, p)):
        d.arrow(a, b)
    d.note("3 stuck at a limit:\nconverged = False", near=r, side="r")
    d.save(OUT / "diagram-ik-restarts.excalidraw")


if __name__ == "__main__":
    loop()
    restarts()
