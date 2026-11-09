# 레슨 03/02 도해: 오차가 kp 로 나뉘어 처짐이 되는 흐름과 모델 오차 방향별 결과를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def flow():
    d = Diagram()
    d.title("Why a soft arm sags")
    a = d.box("Model says\ngravity = ff", 0, 0, "blue")
    b = d.box("Real arm needs\ngravity = tau_g", 0, 1, "yellow")
    c = d.box("Residual\nff - tau_g", 1, 0.5, "red", shape="rectangle")
    e = d.box("Divide by kp\n(the spring)", 2, 0.5, "purple")
    f = d.box("Sag\n= residual / kp", 3, 0.5, "green")
    d.arrow(a, c)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.note("Soft kp = big sag.  Exact model = no sag.", d.margin, d.margin + 60 + 2 * d.ch - 20, size=22)
    d.save(OUT / "diagram-sag-flow.excalidraw")


def cases():
    d = Diagram(cell=(330, 170))
    d.title("Which way does the model error push?")
    m = d.box("Compare the model\nwith the real arm", 0, 0.5, "gray", w=240)
    l = d.box("Model too LIGHT\nff < tau_g", 1, 0, "red", w=250)
    x = d.box("Model exact\nff = tau_g", 1, 1, "green", w=250)
    h = d.box("Model too HEAVY\nff > tau_g", 1, 2, "blue", w=250)
    rl = d.box("Arm droops", 2, 0, "red", w=200)
    rx = d.box("Arm holds", 2, 1, "green", w=200)
    rh = d.box("Arm floats up", 2, 2, "blue", w=200)
    for s, t in ((m, l), (m, x), (m, h), (l, rl), (x, rx), (h, rh)):
        d.arrow(s, t)
    d.save(OUT / "diagram-sag-cases.excalidraw")


if __name__ == "__main__":
    flow()
    cases()
