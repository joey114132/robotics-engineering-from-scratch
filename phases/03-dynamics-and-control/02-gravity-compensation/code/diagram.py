# 레슨 03/02 도해: 오차가 kp 로 나뉘어 처짐이 되는 흐름과 모델 오차 방향별 결과를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def flow():
    d = Diagram(numbered=True)
    d.title("Why a soft arm sags")
    a = d.box("Model feeds\nforward: ff", 0, 0, "blue")
    b = d.box("Gravity really\npulls: tau_g", 0, 1, "yellow")
    c = d.box("Residual\nff - tau_g", 1, 0.5, "red")
    e = d.box("Spring pushes\nback: kp per rad", 2, 0.5, "purple")
    f = d.box("Sag = residual\ndivided by kp", 3, 0.5, "green")
    d.arrow(a, c)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.note("Soft kp = big sag. Exact model = no sag.", near=f, side="b")
    d.save(OUT / "diagram-sag-flow.excalidraw")


def cases():
    d = Diagram()
    d.title("Which way does the model error push?")
    m = d.box("Same arm, kp = 30\nmodel vs real", 0, 1, "gray")
    l = d.box("Too light: ff < tau_g\narm droops 3.7 deg", 1, 0, "red")
    x = d.box("Exact: ff = tau_g\narm holds", 1, 1, "green")
    h = d.box("Too heavy: ff > tau_g\narm floats up 3.8 deg", 1, 2, "red")
    for t in (l, x, h):
        d.arrow(m, t)
    d.save(OUT / "diagram-sag-cases.excalidraw")


if __name__ == "__main__":
    flow()
    cases()
