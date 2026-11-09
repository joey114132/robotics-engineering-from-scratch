# 레슨 07/04 그림: 세 추정값과 두 경로의 주파수 응답, 그리고 tau 에 따른 오차의 U 자 곡선을 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("comp_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY, GREEN = "#0072B2", "#D55E00", "#555555", "#009E73"
ASSETS = HERE.parent / "assets"
DT, B, SA, SG = 0.01, 0.01, 0.05, 0.02  # step (s), gyro bias (rad/s), accel tilt noise (rad), gyro noise (rad/s)


def estimates():
    n = 2000
    t = DT * np.arange(n)[:, None]
    truth, omega = 0.3 * np.sin(1.9 * t), 0.3 * 1.9 * np.cos(1.9 * t)
    gyro, acc = m.sensors(truth, omega, B, SG, SA, np.random.default_rng(4))
    tau = m.best_tau(DT, B, SA)
    est = m.complementary(gyro, acc, DT, tau)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.6), gridspec_kw={"width_ratios": [1.5, 1]})
    a1.plot(t, acc, color=GREY, lw=0.8, alpha=0.7, label="accelerometer only")
    a1.plot(t, m.integrate(gyro, DT), color=ORANGE, label="gyro only")
    a1.plot(t, est, color=BLUE, label=f"complementary, tau = {tau:.2f} s")
    a1.plot(t, truth, "--", color="black", lw=1.6, label="truth")
    a1.set_xlabel("time (s)")
    a1.set_ylabel("tilt (rad)")
    a1.set_title("Fusion tracks the truth, each sensor alone fails")
    a1.set_ylim(-0.8, 0.55)
    a1.legend(loc="lower left", framealpha=0.95, fontsize=11)
    w = np.logspace(-1, 2, 300)
    lp, hp = m.responses(w, tau)
    a2.semilogx(w / (2 * np.pi), abs(lp), color=GREY, label="accelerometer path (low-pass)")
    a2.semilogx(w / (2 * np.pi), abs(hp), color=ORANGE, label="gyro path (high-pass)")
    a2.axvline(m.crossover_hz(tau), color=BLUE, ls="--")
    a2.text(m.crossover_hz(tau) * 1.1, 0.12, f"crossover\n{m.crossover_hz(tau):.2f} Hz", color=BLUE)
    a2.set_xlabel("frequency (Hz)")
    a2.set_ylabel("gain (magnitude)")
    a2.set_title("Trust by frequency")
    a2.legend(loc="center right", framealpha=0.95, fontsize=11)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-tilt-estimates.png", dpi=100)
    plt.close(fig)


def tradeoff():
    n, runs = 6000, 100
    rng = np.random.default_rng(1)
    taus = np.array([0.05, 0.1, 0.2, 0.4, 0.8, 1.5, 3.0])
    gyro, acc = m.sensors(np.zeros((n, 1)), np.zeros((n, 1)), B, 0.0, SA, rng, runs=runs)
    sim = [np.sqrt(np.mean(m.complementary(gyro, acc, DT, tau)[n // 4 :] ** 2)) for tau in taus]
    grid = np.logspace(-1.5, 0.6, 200)
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    ax.loglog(grid, [m.predicted_rmse(g, DT, B, SA) for g in grid], color=BLUE, label="derived: sqrt((tau b)^2 + noise term)")
    ax.loglog(taus, sim, "o", color=ORANGE, label="simulation, 100 runs")
    ax.loglog(grid, grid * B, ":", color=GREY, label="gyro bias term: tau b")
    ax.axhline(SA, color=GREY, ls="--", lw=1.2)
    ax.text(0.03, SA * 0.8, "accelerometer alone", color=GREY)
    ax.set_ylim(2.5e-4, 0.12)
    best = m.best_tau(DT, B, SA)
    ax.axvline(best, color=GREEN, ls="--")
    ax.text(best * 1.08, 0.0022, f"best tau = {best:.2f} s", color=GREEN)
    ax.set_xlabel("filter time constant tau (s)")
    ax.set_ylabel("tilt error, rms (rad)")
    ax.set_title("Too small is noisy, too large drifts")
    ax.legend(loc="lower right", framealpha=0.95, fontsize=11)
    fig.tight_layout()
    fig.savefig(ASSETS / "fig-tau-tradeoff.png", dpi=100)
    plt.close(fig)


if __name__ == "__main__":
    ASSETS.mkdir(exist_ok=True)
    estimates()
    tradeoff()
    print("ok")
