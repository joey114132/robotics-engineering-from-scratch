# 레슨 15/03: planner, controller, drive 의 위치·속도·토크 한계를 비교하는 시작 점검과 어긋남이 낳는 추종 지연
import numpy as np

LAYERS, QUANTITIES = ("planner", "controller", "drive"), ("pos", "vel", "tau")  # outermost request first
ALIGNED = dict(planner=dict(pos=1.5, vel=1.0, tau=None), controller=dict(pos=1.8, vel=1.5, tau=6.0),
               drive=dict(pos=2.0, vel=2.0, tau=8.0))
MISMATCHED = dict(planner=dict(pos=2.2, vel=3.0, tau=None), controller=dict(pos=1.8, vel=3.0, tau=10.0),
                  drive=dict(pos=2.0, vel=1.5, tau=6.0))


def check_limits(L):
    """Every pair of neighbouring layers that both set a limit: the upstream one must not be looser."""
    out = []
    for q in QUANTITIES:
        set_ = [(n, L[n][q]) for n in LAYERS if L[n].get(q) is not None]
        for (a, x), (b, y) in zip(set_, set_[1:]):
            if x > y:
                out.append((q, a, b, x, y, f"{a}.{q} = {x} is looser than {b}.{q} = {y}: {b} wins silently"))
    return out


def require_nested(L):
    """Startup gate: raise once, listing every mismatch."""
    bad = check_limits(L)
    if bad:
        raise ValueError("limit mismatch:\n" + "\n".join(r[-1] for r in bad))


def effective(L, q):
    """The limit the joint really feels, and the layer that owns it."""
    return min((L[n][q], n) for n in LAYERS if L[n].get(q) is not None)


def simulate(L, goal=1.4, T=2.5, dt=1e-3, J=0.5, b=0.2, kp=60.0, kd=6.0):
    """Planner rate-limits a reference, controller runs PD with its own clamps, drive clamps last."""
    P, C, D = (L[n] for n in LAYERS)
    q = qd = ref = 0.0
    err, speed, trace = [], [], []
    for _ in range(int(round(T / dt))):
        ref += np.clip(np.clip(goal, -P["pos"], P["pos"]) - ref, -P["vel"] * dt, P["vel"] * dt)
        qr = np.clip(ref, -C["pos"], C["pos"])
        tau = np.clip(kp * (qr - q) - kd * qd, -C["tau"], C["tau"])
        tau = np.clip(tau, -D["tau"], D["tau"])
        if qd >= D["vel"] or q >= D["pos"]:
            tau = min(tau, 0.0)  # drive refuses to push further out
        if qd <= -D["vel"] or q <= -D["pos"]:
            tau = max(tau, 0.0)
        qd += (tau - b * qd) / J * dt
        q += qd * dt
        err.append(abs(ref - q))
        speed.append(abs(qd))
        trace.append((ref, q))
    return dict(peak_err=max(err), max_speed=max(speed), planner_speed=P["vel"], trace=np.array(trace))


if __name__ == "__main__":
    for name, L in (("aligned", ALIGNED), ("mismatched", MISMATCHED)):
        r = simulate(L)
        print(f"{name:<11} mismatches {len(check_limits(L))}, effective vel {effective(L, 'vel')}, peak lag {r['peak_err']:.2f} rad")
    for row in check_limits(MISMATCHED):
        print("  " + row[-1])
