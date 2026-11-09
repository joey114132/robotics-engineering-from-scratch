# 레슨 06/03 도해: depth 이미지에서 평면을 찾는 파이프라인과 최소제곱이 RANSAC 보다 약한 이유를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def pipeline():
    d = Diagram()
    d.title("From a depth image to the table plane")
    a = d.box("Depth image\n(one z per pixel)", 0, 0.5, "yellow", w=210)
    b = d.box("Unproject\nevery pixel", 1, 0.5, "purple", w=200)
    c = d.box("Voxel grid\none point per cell", 2, 0.5, "purple", w=210)
    e = d.box("RANSAC plane\nthen refit", 3, 0.5, "purple", w=200)
    f = d.box("Table plane\n+ inlier mask", 4, 0.5, "green", w=200)
    for s, t in ((a, b), (b, c), (c, e), (e, f)):
        d.arrow(s, t)
    d.note("The cloud has 19,200 points here; the voxel step keeps the plane and drops most of them.", d.margin, d.margin + 60 + 1.6 * d.ch, size=20)
    d.save(OUT / "diagram-cloud-pipeline.excalidraw")


def ransac():
    d = Diagram(cell=(330, 170))
    d.title("One RANSAC round")
    a = d.box("Pick 3 random\npoints", 0, 0.5, "blue", w=220)
    b = d.box("Plane through\nthem", 1, 0.5, "purple", w=210)
    c = d.box("Count points\nwithin threshold", 2, 0.5, "purple", w=220)
    e = d.box("Most inliers so far?\nKeep it", 3, 0, "green", w=230)
    f = d.box("Repeat N times,\nthen least-squares\non the inliers", 3, 1, "gray", w=230, h=110)
    for s, t in ((a, b), (b, c), (c, e), (c, f)):
        d.arrow(s, t)
    d.save(OUT / "diagram-cloud-ransac.excalidraw")


if __name__ == "__main__":
    pipeline()
    ransac()
