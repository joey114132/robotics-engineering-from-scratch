# 레슨 04/04: 제어 루프 단계별 지연 합, PD 루프의 delay margin, 지연이 phase margin 을 깎는 모양
import numpy as np


def total_latency(stages, period):
    """Sum of stage delays (s) plus half a hold period: a held command lags the ideal one by period/2 on average."""
    return sum(stages.values()) + period / 2


def crossover(kp, kd, J):
    """Gain crossover of L = (kp + kd s) / (J s^2): |L| = 1 gives J^2 w^4 - kd^2 w^2 - kp^2 = 0."""
    return np.sqrt((kd**2 + np.sqrt(kd**4 + 4 * J**2 * kp**2)) / (2 * J**2))


def phase_margin(kp, kd, J, delay=0.0):
    """Radians. The PD zero gives atan(kd*wc/kp); a delay removes wc*delay and leaves the gain untouched."""
    wc = crossover(kp, kd, J)
    return np.arctan(kd * wc / kp) - wc * delay


def delay_margin(kp, kd, J):
    return phase_margin(kp, kd, J) / crossover(kp, kd, J)


def kd_max(delay, kp, J):
    """Largest kd whose delay margin still covers `delay` (grid search; None if no kd does)."""
    kds = np.geomspace(0.01, 1000, 20001)
    ok = [k for k in kds if delay_margin(kp, k, J) >= delay]
    return max(ok) if ok else None


def simulate(kp, kd, J, delay, T=5.0, dt=1e-4, q0=0.1):
    """Double integrator J*qdd = tau with PD acting on q and qd that are `delay` seconds old. Returns q over time."""
    n, lag = int(round(T / dt)), int(round(delay / dt))
    q, qd = np.full(n + 1, q0), np.zeros(n + 1)
    for k in range(n):
        j = max(k - lag, 0)
        qd[k + 1] = qd[k] + dt * (-kp * q[j] - kd * qd[j]) / J
        q[k + 1] = q[k] + dt * qd[k + 1]
    return q


if __name__ == "__main__":
    J, KP, KD = 0.05, 100.0, 2.0
    print("wc", crossover(KP, KD, J), "DM ms", 1e3 * delay_margin(KP, KD, J))
