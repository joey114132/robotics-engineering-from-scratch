# 레슨 12/01 도해: 실제 관절의 신호 경로와 시뮬이 빼먹는 것, 그리고 같은 명령 replay 순서를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram()
    d.title("Real arm vs simple sim: the same command")
    cmd = d.box("Torque command", 0, 0, "blue")
    lag = d.box("Motor lag:\ntorque builds slowly", 1, 0, "red")
    arm = d.box("Hanging arm:\ngravity and friction", 2, 0, "yellow")
    sim = d.box("Simple sim:\nideal arm only", 0, 1, "gray")
    out = d.box("Measured angle", 1, 1, "green")
    dly = d.box("Sensor delay:\nangle read late", 2, 1, "red")
    for a, b in ((cmd, lag), (lag, arm), (arm, dly), (dly, out)):
        d.arrow(a, b)
    d.arrow(cmd, sim, dashed=True)
    d.arrow(sim, out, label="skips 3 steps", dashed=True)
    d.save(OUT / "diagram-real-vs-sim.excalidraw")


def replay():
    d = Diagram(numbered=True)
    d.title("Replay, then rank what is missing")
    rec = d.box("One list of\ncommands", 0, 0, "blue", step=1)
    real = d.box("Run on the\nreal arm", 1, 0, "yellow", step=2)
    sim = d.box("Run on the\nsimulated arm", 2, 0, "gray", step=3)
    gap = d.box("Gap between\nthe two angles", 2, 1, "red", step=4)
    rank = d.box("Drop one effect\nat a time, rank gaps", 1, 1, "green", step=5)
    for a, b in ((rec, real), (real, sim), (sim, gap), (gap, rank)):
        d.arrow(a, b)
    d.save(OUT / "diagram-replay-rank.excalidraw")


if __name__ == "__main__":
    chain()
    replay()
