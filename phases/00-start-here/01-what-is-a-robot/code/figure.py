# 레슨 00/01 그림: 되풀이 고리 자동차는 벽 앞에서 멈추고 센서 없는 자동차는 벽을 지나간다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("robot_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    run = m.drive(seconds=6.0)
    t = [i * m.DT for i in range(len(run["position"]))]
    blind, p = [], 0.0
    for _ in t:
        blind.append(p)
        p = m.act(p, m.SPEED)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2))
    a1.plot(t, run["position"], color=BLUE, lw=2.5, label="loop car (senses the wall)")
    a1.plot(t, blind, color=ORANGE, lw=2, label="blind car (drives 4 s, then stops)")
    a1.axhline(m.WALL, color=GREY, ls="--", lw=1.5)
    a1.text(0.15, m.WALL + 0.12, "wall", color=GREY, fontsize=11)
    a1.set_ylim(-0.1, 4.6)
    a1.set_xlabel("time (s)")
    a1.set_ylabel("car position (m)")
    a1.set_title("The blind car drives through the wall", fontsize=13)
    a1.legend(loc="lower right", fontsize=10)
    a1.grid(alpha=0.3)
    a2.plot(t, run["distance"], color=BLUE, lw=2.5, label="distance sensed (m)")
    a2.step(t, run["speed"], where="post", color=ORANGE, lw=2, label="speed chosen (m/s)")
    a2.axhline(m.STOP_AT, color=GREY, ls="--", lw=1.5)
    a2.text(4.0, m.STOP_AT + 0.08, "stop below this", color=GREY, fontsize=11)
    a2.set_xlabel("time (s)")
    a2.set_ylabel("value (m or m/s)")
    a2.set_title("The loop turns a reading into a decision", fontsize=13)
    a2.legend(loc="upper right", fontsize=10)
    a2.grid(alpha=0.3)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-loop-vs-blind.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, "loop final gap m", round(run["distance"][-1], 2), "blind final x m", round(blind[-1], 2))


if __name__ == "__main__":
    main()
