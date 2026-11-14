# 레슨 15/03 도해: 계층별 한계가 안쪽으로 포개지는 정상 구조와, 한계가 어긋났을 때 조용히 이기는 쪽을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def nested():
    d = Diagram(numbered=True)
    d.title("Healthy: each layer is looser than the one before")
    p = d.box("Planner\nspeed limit 1.0", col=0, row=0, color="blue")
    c = d.box("Controller\nspeed limit 1.5", col=1, row=0, color="purple")
    r = d.box("Drive\nspeed limit 2.0", col=2, row=0, color="gray")
    j = d.box("Joint\nmoves at most 1.0", col=3, row=0, color="yellow")
    for s, t in ((p, c), (c, r), (r, j)):
        d.arrow(s, t)
    d.save(OUT / "diagram-limits-nested.excalidraw")
    return d


def silent():
    d = Diagram(numbered=True)
    d.title("Mismatch: the tightest layer wins and nobody says so")
    p = d.box("Planner asks\nspeed 3.0", col=0, row=0, color="blue")
    c = d.box("Controller allows\nspeed 3.0", col=0, row=1, color="purple")
    r = d.box("Drive allows\nonly 1.5", col=0, row=2, color="red")
    j = d.box("Joint moves\nat 1.5", col=0, row=3, color="yellow")
    chk = d.box("Startup check\nsees 3.0 > 1.5", col=1, row=2, color="green")
    for s, t in ((p, c), (c, r), (r, j)):
        d.arrow(s, t)
    d.arrow(chk, r, dashed=True, label="reports")
    d.save(OUT / "diagram-limits-silent.excalidraw")
    return d


if __name__ == "__main__":
    for dd in (nested(), silent()):
        print(dd.warnings)
