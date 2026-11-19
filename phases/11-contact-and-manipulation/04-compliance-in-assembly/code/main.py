# 레슨 11/04: 2-D thin peg 를 손목 compliance 에 따라 넣는다. 처음엔 tip 만 닿고, 구멍이 좁아지면 두 점 접촉(wedge)이 되어 jam 이 걸리는지 계산한다
import itertools

import numpy as np

P0 = dict(h=5e-4, L=0.05, mu=0.4, alpha=np.radians(3), e=1e-3, kx=1e3, kth=1.0, push=5.0)  # SI units, z points down


def cross2(a, b):
    return a[0] * b[1] - a[1] * b[0]


def wrist(th, p):
    """Wrist wrench (fx, fz, torque about the tip T) on a peg leaning by th, with the tip on the left wall x=-h."""
    r = p["L"] * np.array([np.sin(th), -np.cos(th)])                              # tip to wrist
    Fw = np.array([p["kx"] * (p["e"] + p["h"] - r[0]), p["push"]])               # lateral spring and push force
    return np.array([*Fw, cross2(r, Fw) + p["kth"] * (p["alpha"] - th)])         # plus wrist torsion spring


def free_tilt(p):
    """The lean where the wrist torque about the tip is zero: where the wrist alone would hold the peg."""
    lo, hi = 0.0, np.pi / 4                                                       # torque > 0 at lo, < 0 at hi
    for _ in range(50):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if wrist(mid, p)[2] > 0 else (lo, mid)
    return lo


def wedge(zt, p):
    """Tip T on the left wall at depth zt, peg line through the right mouth edge E=(h, 0): the most the hole lets it lean.
    Returns tilt, wrist wrench, the four friction-cone edge wrenches, and the unit contact wrenches c1, c2 at the sliding limit."""
    h, mu = p["h"], p["mu"]
    th = np.arctan2(2 * h, zt)
    u, n2 = np.array([np.sin(th), -np.cos(th)]), np.array([-np.cos(th), -np.sin(th)])  # up the peg, edge normal
    ET = np.array([2 * h, -zt])                                                   # tip to edge
    wrench = lambda f, r: np.array([f[0], f[1], cross2(r, f)])
    edges = [wrench(np.array([1.0, s * mu]), np.zeros(2)) for s in (-1, 1)] + [wrench(n2 + s * mu * u, ET) for s in (-1, 1)]
    c1, c2 = wrench(np.array([1.0, -mu]), np.zeros(2)), wrench(n2 + mu * u, ET)  # sliding down: friction opposes
    return th, wrist(th, p), np.array(edges), c1, c2


def jammed(wr, edges):
    """True if -wrench is a non-negative combination of friction-cone edge wrenches: contacts can hold the peg."""
    for idx in itertools.combinations(range(len(edges)), 3):
        A = edges[list(idx)].T
        if abs(np.linalg.det(A)) > 1e-12 and (np.linalg.solve(A, -wr) >= -1e-9).all():
            return True
    return False


def insert(p, dz=1e-4):
    """Walk the tip down the wall. The peg leans as the wrist wants until the hole allows less; then the edge E catches it.
    Stops at the first depth where the contacts can hold the wrench (a jam)."""
    th_free, zt, out = free_tilt(p), 2 * p["h"] / np.tan(p["alpha"]), {k: [] for k in ("zt", "N1", "N2", "Fx")}
    done = lambda jam: dict({k: np.array(v) for k, v in out.items()}, jam=jam, th_free=th_free)
    while zt < 0.9 * p["L"]:
        th, wr, edges, c1, c2 = wedge(zt, p)
        if th > th_free:                                                          # only the tip touches
            wr = wrist(th_free, p)
            N1, N2, jam = -wr[0], 0.0, p["push"] <= p["mu"] * -wr[0]             # tip friction alone holds the push
        else:                                                                     # tip and edge: balance sideways and twist
            N2 = -wr[2] / c2[2]
            N1, jam = -wr[0] - N2 * c2[0], jammed(wr, edges)
        if jam:
            return done(zt)
        for k, v in zip(out, (zt, N1, N2, wr[0])):
            out[k].append(v)
        zt += dz
    return done(None)


if __name__ == "__main__":
    for kx in (1e5, 1e4, 1e3, 1e2):
        r = insert(dict(P0, kx=kx))
        print(kx, "jam at depth %.1f mm" % (1e3 * r["jam"]) if r["jam"] else "inserted")
