# 레슨 03/01: 한 주기 동안 홀드되는 댐퍼 명령 tau=-kd*v 의 안정 한계 dt*kd/J < 2
def step_damper(v: float, J: float, kd: float, dt: float) -> float:
    """Pure inertia, torque held for dt: v+ = v + dt*(-kd*v)/J = v*(1 - dt*kd/J)."""
    return v * (1.0 - dt * kd / J)


def simulate_damper(v0: float, J: float, kd: float, dt: float, n: int) -> list[float]:
    v = [v0]
    for _ in range(n):
        v.append(step_damper(v[-1], J, kd, dt))
    return v


def max_smooth_kd(J: float, dt: float) -> float:
    """Exactly here (r = 1) velocity hits zero in one tick (deadbeat). Above it (1 - r) is negative: sign flips."""
    return J / dt


def max_stable_kd(J: float, dt: float) -> float:
    """At r = 2 the factor is -1 (rings forever); above it |1 - r| > 1 and velocity grows."""
    return 2.0 * J / dt


def classify(J: float, kd: float, dt: float) -> str:
    r = dt * kd / J
    if r <= 1.0 + 1e-9:  # r == 1 is deadbeat: zero in one tick, no sign flip
        return "smooth"
    if r < 2.0:
        return "chatter"
    return "divergent"  # r >= 2: never decays


if __name__ == "__main__":
    for kd in (10, 30, 50):
        v = simulate_damper(1.0, 0.02, kd, 0.001, 5)
        print(kd, classify(0.02, kd, 0.001), [round(x, 3) for x in v])
