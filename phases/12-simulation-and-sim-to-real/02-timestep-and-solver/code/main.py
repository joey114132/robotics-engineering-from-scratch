# 레슨 12/02: explicit Euler 와 semi-implicit Euler 를 진자 에너지 drift 와 stiff 접촉 반발 높이로 비교한다
import math

J, K_GRAV = 0.05, 0.2  # the lesson 01 joint without friction: inertia (kg m^2), m*g*l (Nm)
K_CONTACT, G, H0 = 1e4, 9.81, 0.1  # penalty contact stiffness (N/m) for a 1 kg mass, gravity (m/s^2), drop height (m)


def step(method, x, v, acc, dt):
    """One step. explicit: uses the old v for x. semi-implicit: updates v first, then moves x with the new v."""
    if method == "euler":
        return x + dt * v, v + dt * acc(x)
    v = v + dt * acc(x)
    return x + dt * v, v


def pendulum_energy(q, w) -> float:
    return 0.5 * J * w * w + K_GRAV * (1 - math.cos(q))


def pendulum_drift(method, dt, T=10.0, q0=1.0) -> float:
    """Largest |E - E0| / E0 over the run of an undamped pendulum released at q0 (rad)."""
    q, w, e0, worst = q0, 0.0, pendulum_energy(q0, 0.0), 0.0
    for _ in range(round(T / dt)):
        q, w = step(method, q, w, lambda a: -K_GRAV / J * math.sin(a), dt)
        worst = max(worst, abs(pendulum_energy(q, w) - e0) / e0)
    return worst


def rebound_height(method, dt, h0=H0, T=0.6) -> float:
    """Apex (m) after the first bounce of a mass dropped from h0 onto a spring floor at x = 0. Ideal answer: h0."""
    acc = lambda x: -G + K_CONTACT * max(-x, 0.0)
    x, v, hit, apex = h0, 0.0, False, 0.0
    for _ in range(round(T / dt)):
        x, v = step(method, x, v, acc, dt)
        if abs(x) > 1e6:
            return math.inf
        hit = hit or x < 0
        apex = max(apex, x) if hit and x > 0 else apex
    return apex


if __name__ == "__main__":
    for dt in (1e-4, 1e-3, 3e-3, 1.9e-2):
        print(f"dt={dt:g}  rebound euler {rebound_height('euler', dt):.3f} m  semi {rebound_height('semi', dt):.3f} m (ideal {H0} m)")
