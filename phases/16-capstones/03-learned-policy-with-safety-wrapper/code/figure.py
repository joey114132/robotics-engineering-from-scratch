# 레슨 16/03 그림: 깨끗한 도달 실험과, 정책 spike 및 관측 유실 때 wrapper 가 있을 때와 없을 때의 관절 각도와 토크를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("policy_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
TARGET, QLIM = 1.0, 1.3
OUT = HERE.parent / "assets"
T = np.arange(150) * m.DT


def main():
    OUT.mkdir(exist_ok=True)
    pi = m.fit(*m.demos())
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.2))
    for label, policy, safe, style, color in (("expert", m.expert, None, "--", GREY), ("cloned policy", pi, None, "-", BLUE), ("cloned + wrapper", pi, m.Safety(), ":", ORANGE)):
        r = m.rollout(policy, TARGET, safety=safe)
        a1.plot(T, r["q"], style, color=color, lw=2.5, label=label)
        a2.plot(T, r["u"], style, color=color, lw=2.5, label=label)
    a1.axhline(TARGET, color=GREY, lw=1)
    a1.set_title("Cloned policy matches the expert")
    a1.set_ylabel("joint angle (rad)")
    a2.set_title("Torque: wrapper softens only the start")
    a2.set_ylabel("torque command (Nm)")
    for ax in (a1, a2):
        ax.set_xlabel("time (s)")
        ax.grid(alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "fig-policy-result.png", dpi=100)
    plt.close(fig)

    faults = (("Policy spike (+40 Nm at step 30)", dict(glitch={30: 40.0}), (30, 31)), ("Observation lost (steps 10 to 35)", dict(drop=range(10, 36)), (10, 36)))
    fig, axes = plt.subplots(2, 2, figsize=(12, 6.6), sharex=True)
    for col, (title, kw, (k0, k1)) in enumerate(faults):
        for label, safe, color in (("no wrapper", None, ORANGE), ("with wrapper", m.Safety(), BLUE)):
            r = m.rollout(pi, TARGET, safety=safe, **kw)
            axes[0, col].plot(T, r["q"], color=color, lw=2.2, label=label)
            axes[1, col].plot(T, r["u"], color=color, lw=2.2, label=label)
            if safe:
                n = r["n"]
        axes[0, col].axhline(QLIM, color=GREY, ls="--", label=f"joint limit {QLIM} rad")
        axes[0, col].set_title(title, fontsize=11)
        axes[1, col].set_title(f"wrapper interventions: clip {n['clip']}, rate limit {n['rate']}, hold {n['hold']}", fontsize=10)
        for ax in axes[:, col]:
            ax.axvspan(k0 * m.DT, k1 * m.DT, color="#dddddd", alpha=0.6)
            ax.grid(alpha=0.3)
        axes[1, col].set_xlabel("time (s)")
    axes[0, 0].set_ylabel("joint angle (rad)")
    axes[1, 0].set_ylabel("torque command (Nm)")
    axes[0, 0].legend(loc="lower right", fontsize=9)
    axes[0, 1].legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(OUT / "fig-policy-faults.png", dpi=100)
    print(OUT)


if __name__ == "__main__":
    main()
