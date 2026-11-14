# 레슨 06/03 도해: depth 이미지에서 평면을 찾는 파이프라인과 최소제곱이 RANSAC 보다 약한 이유를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram(numbered=True)
    d.title("From a depth image to the table plane")
    a = d.box("Depth image\n19,200 pixels", col=0, row=0, color="yellow", step=1)
    b = d.box("Unproject\nevery pixel", col=1, row=0, color="purple", step=2)
    c = d.box("Voxel grid\none point per cube", col=2, row=0, color="purple", step=3)
    e = d.box("RANSAC plane\nthen refit", col=2, row=1, color="purple", step=4)
    f = d.box("Table plane\n+ inlier mask", col=1, row=1, color="green", step=5)
    for s, t in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-cloud-pipeline.excalidraw")
    return d.warnings


def ransac():
    d = Diagram(numbered=True)
    d.title("One RANSAC round")
    a = d.box("Pick 3 random\npoints", col=0, row=0, color="blue")
    b = d.box("Plane through\nthem", col=1, row=0, color="purple")
    c = d.box("Count points\nnear the plane", col=2, row=0, color="purple")
    e = d.box("Best so far?\nKeep it", col=2, row=1, color="green")
    f = d.box("After 150 rounds:\nrefit on inliers", col=2, row=2, color="gray")
    for s, t in ((a, b), (b, c), (c, e)):
        d.arrow(s, t)
    d.arrow(e, a, label="next round", dashed=True)
    d.arrow(e, f)
    d.save(OUT / "diagram-cloud-ransac.excalidraw")
    return d.warnings


if __name__ == "__main__":
    print(pipeline(), ransac())
