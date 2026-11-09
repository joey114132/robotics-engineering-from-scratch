# 레슨 16/01: 2링크 팔 pick-and-place 시뮬레이션. IK 웨이포인트, quintic 궤적, PD + 중력 feedforward, 놓는 점 오차로 pass/fail
import numpy as np

G, DT, KP, KD, TOL = 9.81, 1e-3, 150.0, 12.0, 0.005
L = (0.4, 0.4)
P = dict(m1=2.0, m2=1.0, l1=0.4, lc1=0.2, lc2=0.2)


def fk(q):
    return np.array([L[0] * np.cos(q[0]) + L[1] * np.cos(q[0] + q[1]), L[0] * np.sin(q[0]) + L[1] * np.sin(q[0] + q[1])])


def ik(p):
    """Elbow-down (q2 >= 0) solution by the law of cosines (lesson 02/02)."""
    x, y = p
    c2 = (x * x + y * y - L[0] ** 2 - L[1] ** 2) / (2 * L[0] * L[1])
    if abs(c2) > 1:
        raise ValueError(f"unreachable: {p}")
    s2 = np.sqrt(1 - c2 * c2)
    return np.array([np.arctan2(y, x) - np.arctan2(L[1] * s2, L[0] + L[1] * c2), np.arctan2(s2, c2)])


def gravity(q):
    """Holding torques (lesson 03/02). Angles from the horizontal."""
    t2 = P["m2"] * P["lc2"] * G * np.cos(q[0] + q[1])
    return np.array([(P["m1"] * P["lc1"] + P["m2"] * P["l1"]) * G * np.cos(q[0]) + t2, t2])


def inertia(q):
    """Mass matrix of two uniform rods: I = m (2 lc)^2 / 12 about each centre of mass."""
    i1, i2 = P["m1"] * (2 * P["lc1"]) ** 2 / 12, P["m2"] * (2 * P["lc2"]) ** 2 / 12
    m12 = P["m2"] * (P["lc2"] ** 2 + P["l1"] * P["lc2"] * np.cos(q[1])) + i2
    m11 = P["m1"] * P["lc1"] ** 2 + P["m2"] * (P["l1"] ** 2 + P["lc2"] ** 2 + 2 * P["l1"] * P["lc2"] * np.cos(q[1])) + i1 + i2
    return np.array([[m11, m12], [m12, P["m2"] * P["lc2"] ** 2 + i2]])


def step(q, v, tau, dt=DT):
    """One semi-implicit Euler step of M(q) a + C(q, v) + g(q) = tau."""
    h = P["m2"] * P["l1"] * P["lc2"] * np.sin(q[1])
    coriolis = np.array([-h * v[1] * (2 * v[0] + v[1]), h * v[0] ** 2])
    v = v + dt * np.linalg.solve(inertia(q), tau - coriolis - gravity(q))
    return q + dt * v, v


def reference(wp, T):
    """Quintic segment of duration T between consecutive joint waypoints: zero velocity and acceleration at each one (lesson 09/01)."""
    def f(t):
        i = min(int(t // T), len(wp) - 2)
        u = min((t - i * T) / T, 1.0)
        d = wp[i + 1] - wp[i]
        s, ds, dds = 10 * u**3 - 15 * u**4 + 6 * u**5, (30 * u**2 - 60 * u**3 + 30 * u**4) / T, (60 * u - 180 * u**2 + 120 * u**3) / T**2
        return wp[i] + d * s, d * ds, d * dds
    return f


def run(a, b, ff=1.0, kp=KP, kd=KD, T=1.0, settle=0.5):
    """Home, hover over A, pick A, lift, hover over B, place B. ff scales the gravity feedforward (0 removes it)."""
    pts = [(0.40, 0.40), (a[0], a[1] + 0.1), a, (a[0], a[1] + 0.1), (b[0], b[1] + 0.1), b]
    wp = [ik(p) for p in pts]
    ref, q, v = reference(wp, T), wp[0].copy(), np.zeros(2)
    n = int((5 * T + settle) / DT)
    Q, QR = np.zeros((n, 2)), np.zeros((n, 2))
    for k in range(n):
        qd, vd, _ = ref(k * DT)
        q, v = step(q, v, ff * gravity(qd) + kp * (qd - q) + kd * (vd - v))
        Q[k], QR[k] = q, qd
    tip = np.array([fk(x) for x in Q])
    pick_err = float(np.linalg.norm(tip[int(2 * T / DT) - 1] - a))
    place_err = float(np.linalg.norm(tip[-1] - b))
    return dict(t=np.arange(n) * DT, q=Q, q_ref=QR, tip=tip, pick_err=pick_err, place_err=place_err, passed=place_err < TOL, pts=pts)


if __name__ == "__main__":
    for ff in (1.0, 0.0):
        r = run((0.50, 0.10), (0.15, 0.50), ff)
        print(f"ff={ff}: pick error {r['pick_err'] * 1000:.2f} mm, place error {r['place_err'] * 1000:.2f} mm, {'PASS' if r['passed'] else 'FAIL'}")
