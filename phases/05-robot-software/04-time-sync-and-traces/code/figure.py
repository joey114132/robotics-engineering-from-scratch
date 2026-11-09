# 레슨 05/04 그림: 한 번 잰 offset 대 가장 짧은 왕복을 고른 offset 의 오차, 그리고 offset 에 따른 센서 순서 오류를 그린다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("time_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
A = [0.02 * i for i in range(50)]
B = [0.02 * i + 0.01 for i in range(50)]


def main():
    rng = np.random.default_rng(0)
    one, best = [], []
    for _ in range(400):
        s = [m.exchange(0.05, 0.005 + rng.exponential(0.005), 0.005 + rng.exponential(0.005)) for _ in range(8)]
        one.append((m.estimate(*s[0])[0] - 0.05) * 1e3)
        best.append((m.best_offset(s) - 0.05) * 1e3)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6))
    bins = np.linspace(-14, 14, 57)
    a1.hist(one, bins, color=ORANGE, alpha=0.75, label=f"one exchange (spread {np.std(one):.1f} ms)")
    a1.hist(best, bins, color=BLUE, alpha=0.75, label=f"lowest delay of 8 ({np.std(best):.1f} ms)")
    a1.set_xlabel("offset estimate minus true offset (ms)")
    a1.set_ylabel("trials")
    a1.set_title("Pick the exchange with the smallest round trip")
    a1.legend(loc="upper right")

    offs = np.linspace(0, 0.015, 61)
    raw = [m.order_errors(A, B, o) for o in offs]
    fixed = [m.order_errors(A, B, o, correction=o + 0.001) for o in offs]  # estimate is 1 ms off
    a2.plot(offs * 1e3, raw, color=ORANGE, label="stamps used as they are")
    a2.plot(offs * 1e3, fixed, color=BLUE, label="offset estimate removed (1 ms error)")
    a2.axvline(10, color=GREY, ls=":")
    a2.text(10.3, 20, "10 ms: sensor gap", color=GREY)
    a2.set_xlabel("clock offset of sensor B (ms)")
    a2.set_ylabel("slots in the wrong order (of 100)")
    a2.set_title("A clock offset past the gap reorders sensors")
    a2.set_ylim(-5, 150)
    a2.legend(loc="upper left")
    fig.tight_layout()
    out = HERE.parent / "assets" / "fig-time-sync.png"
    out.parent.mkdir(exist_ok=True)
    fig.savefig(out, dpi=100)
    print(out, np.std(one), np.std(best))


if __name__ == "__main__":
    main()
