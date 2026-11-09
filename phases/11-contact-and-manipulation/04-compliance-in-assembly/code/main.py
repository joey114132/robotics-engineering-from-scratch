# 레슨 11/04: 2-D thin peg 의 두 점 접촉(wedge) 준정적 해석으로 손목 compliance 에 따른 jamming 과 접촉력을 계산한다
import itertools

import numpy as np

P0 = dict(h=5e-4, L=0.05, mu=0.4, alpha=np.radians(3), e=1e-3, kx=1e3, kth=1.0, push=5.0)  # SI units, z points down


def cross2(a, b):
    return a[0] * b[1] - a[1] * b[0]


def wedge(zt, p):
    """Tip T on the left wall (x=-h, depth zt), peg line through the right mouth edge E=(h, 0).
    Returns tilt, wrist wrench (fx, fz, torque about T), unit contact wrenches c1, c2 at the sliding limit, manifold tangent."""
    h, L, mu = p["h"], p["L"], p["mu"]
    th = np.arctan2(2 * h, zt)
    u, n2 = np.array([np.sin(th), -np.cos(th)]), np.array([-np.cos(th), -np.sin(th)])  # up the peg, edge normal
    T, E = np.array([-h, zt]), np.array([h, 0.0])
    W = T + L * u
    Fw = np.array([p["kx"] * (p["e"] - W[0]), p["push"]])                      # lateral spring and push force
    wr = np.array([*Fw, cross2(W - T, Fw) + p["kth"] * (p["alpha"] - th)])    # plus wrist torsion spring
    wrench = lambda f, r: np.array([f[0], f[1], cross2(r, f)])
    edges = [wrench(np.array([1.0, s * mu]), np.zeros(2)) for s in (-1, 1)] + [wrench(n2 + s * mu * u, E - T) for s in (-1, 1)]
    c1, c2 = wrench(np.array([1.0, -mu]), np.zeros(2)), wrench(n2 + mu * u, E - T)  # sliding down: friction opposes
    tau = np.array([0.0, 1.0, -2 * h / (zt**2 + 4 * h**2)])                    # d(x_T, z_T, tilt) / d zt
    return th, wr, np.array(edges), c1, c2, tau


def jammed(wr, edges):
    """True if -wrench is a non-negative combination of friction-cone edge wrenches: contacts can hold the peg."""
    for idx in itertools.combinations(range(len(edges)), 3):
        A = edges[list(idx)].T
        if abs(np.linalg.det(A)) > 1e-12 and (np.linalg.solve(A, -wr) >= -1e-9).all():
            return True
    return False


def insert(p, dz=1e-4):
    """Walk the tip down the wall. Stops at the first depth where the contacts can hold the wrench (a jam)."""
    zt, out = 2 * p["h"] / np.tan(p["alpha"]), {k: [] for k in ("zt", "N1", "N2", "Fx")}
    while zt < 0.9 * p["L"]:
        _, wr, edges, c1, c2, tau = wedge(zt, p)
        if jammed(wr, edges):
            return dict({k: np.array(v) for k, v in out.items()}, jam=zt)
        N1, N2, _ = np.linalg.solve(np.c_[c1, c2, -tau], -wr)                  # normal forces while sliding
        for k, v in zip(out, (zt, N1, N2, wr[0])):
            out[k].append(v)
        zt += dz
    return dict({k: np.array(v) for k, v in out.items()}, jam=None)


if __name__ == "__main__":
    for kx in (1e5, 1e4, 1e3, 1e2):
        r = insert(dict(P0, kx=kx))
        print(kx, "jam at depth %.1f mm" % (1e3 * r["jam"]) if r["jam"] else "inserted")
