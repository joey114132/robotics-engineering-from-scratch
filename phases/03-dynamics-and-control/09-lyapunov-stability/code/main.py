# 레슨 03/09: PD 제어 진자의 에너지형 함수 V 를 만들고 상태를 무작위로 뽑아 dV/dt <= 0 을 검사하며 지연을 넣어 깨 본다
import numpy as np

G_L = 9.81  # g / l for a 1 m pendulum
DEFAULT = dict(c=0.1, kp=10.0, kd=2.0)


def f(x, p, vel_cmd=None):
    """State (angle, rate). Acceleration = gravity + damping c + PD command. vel_cmd is the rate the controller sees."""
    v = x[1] if vel_cmd is None else vel_cmd
    return np.array([x[1], -G_L * np.sin(x[0]) - p["c"] * x[1] - p["kp"] * x[0] - p["kd"] * v])


def V(x, p):
    """Kinetic + gravity potential + the PD spring's potential: zero only at the origin."""
    return 0.5 * x[1] ** 2 + G_L * (1 - np.cos(x[0])) + 0.5 * p["kp"] * x[0] ** 2


def vdot(x, p, h=1e-6):
    """dV/dt along the dynamics: grad V . f(x), gradient by central differences."""
    grad = np.array([(V(x + h * e, p) - V(x - h * e, p)) / (2 * h) for e in np.eye(2)])
    return float(grad @ f(x, p))


def check(p, n=20000, box=(3.0, 8.0), seed=0):
    """Sample states in the box. Returns (largest dV/dt, the state where it happens)."""
    rng = np.random.default_rng(seed)
    xs = rng.uniform(-1, 1, (n, 2)) * np.array(box)
    vd = np.array([vdot(x, p) for x in xs])
    i = int(vd.argmax())
    return float(vd[i]), xs[i]


def simulate(p, x0, T=10.0, dt=1e-3, delay=0.0):
    """Semi-implicit Euler. The controller sees the rate from `delay` seconds ago. Returns V along the run."""
    lag, x, out = int(round(delay / dt)), np.array(x0, float), []
    hist = [x[1]] * (lag + 1)
    for _ in range(int(T / dt)):
        out.append(V(x, p))
        a = f(x, p, vel_cmd=hist[0])[1]
        x = np.array([x[0] + dt * (x[1] + dt * a), x[1] + dt * a])
        hist = hist[1:] + [x[1]]
    return np.array(out)


if __name__ == "__main__":
    print(check(DEFAULT)[0], check(dict(DEFAULT, kd=-1.0))[0])
