# 레슨 00/04 도해: 팔의 부품(관절과 링크)과, 각도와 길이가 "옆으로 얼마, 위로 얼마"가 되는 길을 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def parts():
    d = Diagram()
    d.title("An arm is bars and hinges")
    base = d.box("Base\nfixed", col=0, row=0, color="gray")
    j1 = d.box("Joint 1\nhinge", col=1, row=0, color="yellow")
    l1 = d.box("Link 1\nrigid bar", col=2, row=0, color="blue")
    j2 = d.box("Joint 2\nhinge", col=2, row=1, color="yellow")
    l2 = d.box("Link 2\nrigid bar", col=1, row=1, color="blue")
    hand = d.box("Hand\nthe tip", col=0, row=1, color="green")
    for s, t in ((base, j1), (j1, l1), (l1, j2), (j2, l2), (l2, hand)):
        d.arrow(s, t)
    d.note("A joint turns. A link never bends.", near=l2, side="b")
    d.save(OUT / "diagram-arm-parts.excalidraw")


def recipe():
    d = Diagram()
    d.title("Angle and length to hand position")
    ang = d.box("Joint angle", col=0, row=0, color="blue")
    ln = d.box("Link length", col=0, row=1, color="blue")
    cs = d.box("cos and sin", col=1, row=0.5, color="purple")
    across = d.box("How far\nacross", col=2, row=0, color="green")
    up = d.box("How far\nup", col=2, row=1, color="green")
    for s, t in ((ang, cs), (ln, cs), (cs, across), (cs, up)):
        d.arrow(s, t)
    d.note("The hand is one point: across and up", near=up, side="b")
    d.save(OUT / "diagram-angle-to-position.excalidraw")


if __name__ == "__main__":
    parts()
    recipe()
