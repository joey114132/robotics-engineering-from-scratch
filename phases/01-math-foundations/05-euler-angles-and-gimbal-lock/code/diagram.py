# 레슨 01/05 도해: 세 고리 중 둘이 한 줄로 서는 gimbal lock 과, 매끄러운 기울임이 180도 점프로 읽히는 과정을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def rings():
    d = Diagram(numbered=True)
    d.title("Three rings, one hole")
    y = d.box("Yaw ring\nouter", 0, 0, "blue", step=1)
    p = d.box("Pitch ring\nmiddle", 1, 0, "purple", step=2)
    r = d.box("Roll ring\ninner", 2, 0, "green", step=3)
    bad = d.box("At pitch 90\nrings align", 1, 1, "red", step=4)
    lost = d.box("Two rings,\none line", 2, 1, "yellow", step=5)
    for a, b in ((y, p), (p, r), (p, bad), (bad, lost)):
        d.arrow(a, b)
    d.save(OUT / "diagram-gimbal-rings.excalidraw")


def jump():
    d = Diagram(numbered=True)
    d.title("A smooth tilt that reads as a jump")
    a = d.box("Tilt past\n90 deg", 0, 0, "yellow", step=1)
    b = d.box("Reader flips\nspelling", 1, 0, "blue", step=2)
    c = d.box("Roll, yaw\njump 180", 2, 0, "red", step=3)
    e = d.box("Store R or\nquaternion", 2, 1, "green", step=4)
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.save(OUT / "diagram-angle-jump.excalidraw")


if __name__ == "__main__":
    rings()
    jump()
