# 레슨 12/01 도해: 실제 관절의 신호 경로와 시뮬이 빼먹는 것, 그리고 같은 명령 replay 순서를 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def chain():
    d = Diagram(cell=(290, 170))
    d.title("What the real joint does that a simple sim skips")
    cmd = d.box("Torque\ncommand", 0, 0, "blue", w=190)
    lag = d.box("Motor lag\n(torque arrives late)", 1, 0, "red", w=230)
    joint = d.box("Joint: inertia,\ngravity, friction", 2, 0, "yellow", w=230)
    delay = d.box("Sensor delay\n(angle read late)", 3, 0, "red", w=230)
    out = d.box("Measured\nangle", 3, 1.1, "green", w=190)
    sim = d.box("Simple sim:\nno lag, no friction,\nno delay", 1, 1.1, "gray", w=260, h=110)
    for a, b in ((cmd, lag), (lag, joint), (joint, delay)):
        d.arrow(a, b)
    d.arrow(delay, out)
    d.arrow(sim, out, label="same command, shorter path", dashed=True)
    d.save(OUT / "diagram-real-vs-sim.excalidraw")


def replay():
    d = Diagram(cell=(300, 170))
    d.title("Replay the same commands, then rank what is missing")
    rec = d.box("One list of\nopen-loop commands", 0, 0.5, "blue", w=230)
    real = d.box("Real plant", 1, 0, "yellow", w=210)
    sim = d.box("Simulated plant", 1, 1, "gray", w=210)
    gap = d.box("Divergence\nover time", 2, 0.5, "red", w=210)
    rank = d.box("Remove one effect\nat a time, rank cost", 3, 0.5, "green", w=250)
    for a, b in ((rec, real), (rec, sim), (real, gap), (sim, gap), (gap, rank)):
        d.arrow(a, b)
    d.save(OUT / "diagram-replay-rank.excalidraw")


if __name__ == "__main__":
    chain()
    replay()
