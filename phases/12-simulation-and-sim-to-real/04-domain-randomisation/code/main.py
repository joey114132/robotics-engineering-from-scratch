# 레슨 12/04: 고정 PD controller 를 무작위 plant 묶음에서 한꺼번에 평가하고, 범위에 맞춰 gain 을 고르는 격자 탐색을 만든다
import numpy as np

NOM = dict(J=0.05, b=0.02, c=0.05, k=0.2, Tm=0.03, dl=0.02)  # lesson 12/01 joint; dl = sensor delay (s)
DT, EPS, T, REF, UMAX = 2e-3, 0.01, 3.0, 1.0, 1.0  # RK4 step (s), Coulomb smoothing, run length (s), step target (rad), torque limit (Nm)
BAND, SETTLE, OVERSHOOT, FAIL = 0.05, 0.8, 1.05, 2.0  # success: inside +-0.05 rad by 0.8 s, peak under 1.05 rad. A failed run costs 2 s.
KPS, KDS = np.geomspace(2, 200, 18), np.geomspace(0.1, 4, 18)  # gain grid: position (Nm/rad) and damping (Nm s/rad)


def sample(width, n, rng) -> dict:
    """n plants, every parameter scaled by 1 + width * U(-1, 1). width 0 is the nominal plant."""
    return {k: v * (1 + width * rng.uniform(-1, 1, n)) for k, v in NOM.items()}


def simulate(P, kp, kd) -> np.ndarray:
    """RK4 step response of M plants at once. Returns q with shape (steps, M). The controller sees q and w late by the sensor delay."""
    M = len(kp)
    q = w = tm = np.zeros(M)
    qs, ws, d, cols = np.zeros((round(T / DT), M)), np.zeros((round(T / DT), M)), np.round(P["dl"] / DT).astype(int), np.arange(M)
    f = lambda q, w, tm, u: (w, (tm - P["b"] * w - P["c"] * np.tanh(w / EPS) - P["k"] * np.sin(q)) / P["J"], (u - tm) / P["Tm"])
    for i in range(len(qs)):
        qs[i], ws[i] = q, w
        j = np.maximum(i - d, 0)
        u = np.clip(kp * (REF - qs[j, cols]) - kd * ws[j, cols] + NOM["k"] * np.sin(qs[j, cols]), -UMAX, UMAX)
        s = (q, w, tm)
        k1 = f(*s, u)
        k2 = f(*(a + 0.5 * DT * b for a, b in zip(s, k1)), u)
        k3 = f(*(a + 0.5 * DT * b for a, b in zip(s, k2)), u)
        k4 = f(*(a + DT * b for a, b in zip(s, k3)), u)
        q, w, tm = (a + DT / 6 * (b + 2 * c + 2 * e + g) for a, b, c, e, g in zip(s, k1, k2, k3, k4))
    return qs


def score(q):
    """Per run: success flag and settle time (s, last time outside the band). Success needs the settle and overshoot limits."""
    out = np.abs(q - REF) > BAND
    settle = (len(q) - np.argmax(out[::-1], 0)) * DT * out.any(0)
    return (settle <= SETTLE) & (q.max(0) < OVERSHOOT), settle


def evaluate(kp, kd, width, n, seed):
    """Fixed gains on n random plants: (success rate, mean cost) where a failure costs FAIL seconds."""
    ok, st = score(simulate(sample(width, n, np.random.default_rng(seed)), np.full(n, kp), np.full(n, kd)))
    return float(ok.mean()), float(np.where(ok, st, FAIL).mean())


def tune(width, n, seed, kps=KPS, kds=KDS):
    """Grid search the gain pair with the lowest mean cost over n random plants drawn at this width."""
    kp, kd = (g.ravel() for g in np.meshgrid(kps, kds, indexing="ij"))
    P = sample(width, n, np.random.default_rng(seed))
    ok, st = score(simulate({k: np.tile(v, len(kp)) for k, v in P.items()}, np.repeat(kp, n), np.repeat(kd, n)))
    cost = np.where(ok, st, FAIL).reshape(len(kp), n).mean(1)
    return float(kp[cost.argmin()]), float(kd[cost.argmin()])


if __name__ == "__main__":
    for w in (0.0, 0.3, 0.6):
        kp, kd = tune(w, 1 if w == 0 else 40, 1)
        print(f"tuned on width {w}: kp {kp:.1f} kd {kd:.2f} -> success on width 0.3 = {evaluate(kp, kd, 0.3, 300, 7)[0]:.2f}")
