# 레슨 00/04 그림: queue depth 별로 전달된 메시지의 나이와 전달, 폐기, 대기 개수를 비교한다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("bus_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY, SKY = "#0072B2", "#D55E00", "#555555", "#56B4E9"


def main():
    depths, secs = (1, 10, 50), 10.0
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2), gridspec_kw={"width_ratios": [1.3, 1]})
    runs = {d: m.run(100, 40, d, secs) for d in depths}
    for d, c in zip(depths, (BLUE, SKY, ORANGE)):
        a1.plot(np.arange(len(runs[d]["ages"])) / 40, runs[d]["ages"] * 1000, color=c, lw=2, label=f"depth {d}")
    a1.set_xlabel("time (s)")
    a1.set_ylabel("age of message read (ms)")
    a1.set_title("A deeper queue hands over staler data", fontsize=13)
    a1.legend(loc="center right", fontsize=10)
    a1.grid(alpha=0.3)
    x = np.arange(len(depths))
    deliv = np.array([runs[d]["delivered"] for d in depths])
    drop = np.array([runs[d]["dropped"] for d in depths])
    queued = np.array([runs[d]["published"] for d in depths]) - deliv - drop
    a2.bar(x, deliv, color=BLUE, label="delivered")
    a2.bar(x, drop, bottom=deliv, color=ORANGE, label="dropped")
    a2.bar(x, queued, bottom=deliv + drop, color=GREY, label="still queued")
    a2.set_xticks(x, [f"depth {d}" for d in depths])
    a2.set_ylabel("messages out of 1000 published")
    a2.set_title("Depth does not fix a slow subscriber", fontsize=13)
    a2.set_ylim(0, 1250)
    a2.legend(loc="upper center", ncol=3, fontsize=9)
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-queue-depth.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, deliv, drop, queued)


if __name__ == "__main__":
    main()
