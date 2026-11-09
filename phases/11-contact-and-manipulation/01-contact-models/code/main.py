# 레슨 11/01: 경사면 위 블록의 페널티 법선력 + 쿨롱 마찰 시뮬레이션과 stick/slip 조건 tan(theta) vs mu
import numpy as np

G, M, DT = 9.81, 1.0, 1e-4
K, C = 1e4, 140.0       # normal spring (N/m) and damper (N s/m), about 0.7 of critical
KT, CT = 1e4, 200.0     # tangential "bristle" spring and damper


def critical_angle(mu: float) -> float:
    return float(np.arctan(mu))


def slides(theta: float, mu: float) -> bool:
    return bool(np.tan(theta) > mu)


def slip_accel(theta: float, mu: float) -> float:
    """Acceleration down the slope once sliding: g (sin t - mu cos t)."""
    return G * (np.sin(theta) - mu * np.cos(theta))


def simulate(theta: float, mu: float, T: float = 2.0) -> dict:
    """Block starts touching the plane at rest. s along the slope (down is +), n above the plane."""
    s = v = n = nv = anchor = 0.0
    out = {k: np.zeros(int(T / DT)) for k in ("t", "s", "v", "fn", "ft")}
    for i in range(out["t"].size):
        pen = max(-n, 0.0)
        fn = max(K * pen - C * nv, 0.0) if pen > 0 else 0.0   # penalty spring-damper, never pulls
        ft = 0.0
        if pen > 0:
            ft = -KT * (s - anchor) - CT * v                  # stick: tangential spring to an anchor
            cap = mu * fn
            if abs(ft) > cap:                                 # outside the cone: slip, drag the anchor
                ft = np.sign(ft) * cap
                anchor = s + ft / KT
        else:
            anchor = s
        v += (G * np.sin(theta) + ft / M) * DT
        nv += (-G * np.cos(theta) + fn / M) * DT
        s, n = s + v * DT, n + nv * DT
        for k, x in zip(out, (i * DT, s, v, fn, ft)):
            out[k][i] = x
    return out


if __name__ == "__main__":
    for deg in (15, 25, 28, 35):
        r = simulate(np.radians(deg), 0.5)
        print(deg, "stuck" if abs(r["v"][-1]) < 0.05 else f"slides, v={r['v'][-1]:.2f}")
