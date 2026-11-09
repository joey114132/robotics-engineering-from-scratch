# 레슨 05/01 그림: 신뢰도 조합별 전달 비율과 큐 깊이에 따른 유실을 PNG 한 장으로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("qos_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"


def main():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6))
    combos = [("reliable", "reliable"), ("reliable", "best_effort"), ("best_effort", "best_effort"), ("best_effort", "reliable")]
    frac = []
    for p, s in combos:
        r = m.run(m.Qos(p), m.Qos(s, depth=50), [1] * 400, link_loss=0.2, seed=1)
        frac.append(100 * r["delivered"] / r["published"])
    labels = [f"pub {p.replace('_', ' ')}\nsub {s.replace('_', ' ')}" for p, s in combos]
    a1.bar(range(4), frac, color=[BLUE, BLUE, BLUE, ORANGE])
    for i, f in enumerate(frac):
        a1.text(i, f + 2, f"{f:.0f}%", ha="center")
    a1.set_xticks(range(4))
    a1.set_xticklabels(labels, fontsize=11)
    a1.set_ylim(0, 118)
    a1.set_ylabel("messages delivered (%)")
    a1.set_title("Best effort publisher, reliable subscriber: 0%")

    depths = list(range(1, 13))
    burst = [8] + [0] * 19
    b = [m.run(m.Qos(), m.Qos(depth=d), burst * 10)["dropped"] / 80 * 100 for d in depths]
    o = [m.run(m.Qos(), m.Qos(depth=d), [2] * 80)["dropped"] / 160 * 100 for d in depths]
    a2.plot(depths, b, "o-", color=BLUE, label="burst of 8 every 20 ticks")
    a2.plot(depths, o, "s-", color=ORANGE, label="2 msgs per tick, 1 consumed")
    a2.axhline(0, color=GREY, lw=1)
    a2.set_xlabel("queue depth (messages)")
    a2.set_ylabel("messages dropped (%)")
    a2.set_title("Depth fixes bursts, not overload")
    a2.legend(loc="upper right")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-qos-delivery.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out)


if __name__ == "__main__":
    main()
