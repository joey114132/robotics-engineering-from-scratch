# 레슨 15/01: 1자유도 관절 PD 루프에 결함 다섯 가지를 주입하고 피해와 감지 시각을 잰다
import numpy as np

FAULTS = ("none", "stuck", "dropout", "delay", "saturation", "wrong_sign")
P = dict(J=0.5, b=0.2, kp=40.0, kd=4.0, tau_max=10.0, q_ref=1.0, q_lim=2.0)


def simulate(fault="none", T=3.0, dt=1e-3, t_fault=0.3, delay=0.1, sat=0.5, **over):
    """Rows of (t, q, qd, tau, reading). Sensor faults start at t_fault; saturation and wrong sign exist from tick 0."""
    p = {**P, **over}
    t0 = 0.0 if fault in ("saturation", "wrong_sign") else t_fault
    q = qd = 0.0
    held, lag = None, [(0.0, 0.0)] * int(round(delay / dt))
    rows = np.zeros((int(round(T / dt)), 5))
    for i in range(len(rows)):
        t = i * dt
        on = t >= t0
        qm, qdm = q, qd
        if fault == "stuck" and on:
            held = held or (q, qd)
            qm, qdm = held
        elif fault == "dropout" and on and t < t0 + 0.3:
            qm, qdm = 0.0, 0.0
        elif fault == "delay":
            lag.append((q, qd))
            old = lag.pop(0)
            if on:
                qm, qdm = old
        tau = float(np.clip(p["kp"] * (p["q_ref"] - qm) - p["kd"] * qdm, -p["tau_max"], p["tau_max"]))
        if fault == "saturation":
            tau = float(np.clip(tau, -sat, sat))
        if fault == "wrong_sign":
            tau = -tau
        qd += (tau - p["b"] * qd) / p["J"] * dt  # semi-implicit Euler
        q += qd * dt
        if abs(q) >= p["q_lim"]:  # hard stop
            q, qd = np.copysign(p["q_lim"], q), 0.0
        rows[i] = (t, q, qd, tau, qm)
    return rows


def metrics(run, q_ref=P["q_ref"], q_lim=P["q_lim"]):
    """How bad: did the true joint reach the limit, when, and how far from the target does it end."""
    hit = np.nonzero(np.abs(run[:, 1]) >= q_lim)[0]
    return dict(peak=float(np.abs(run[:, 1]).max()), final_err=float(abs(run[-1, 1] - q_ref)),
                hit=bool(len(hit)), t_limit=float(run[hit[0], 0]) if len(hit) else None)


def alarm_time(run, q_ref=P["q_ref"], dt=1e-3):
    """How detectable: first time any cheap check on the controller's own signals trips, else None."""
    t, tau, r = run[:, 0], run[:, 3], run[:, 4]
    e, w, g = np.abs(q_ref - r), int(0.05 / dt), int(0.1 / dt)
    for i in range(g, len(t)):
        frozen = np.ptp(r[i - w:i + 1]) == 0 and abs(tau[i]) > 0.5  # reading flat while torque is applied
        jump = abs(r[i] - r[i - 1]) > 0.3  # reading teleports in one tick
        growing = e[i] - e[i - g] > 0.3  # error got much worse in 100 ms
        late = t[i] >= 2.0 and e[i] > 0.1  # still not at the target after 2 s
        if frozen or jump or growing or late:
            return float(t[i])
    return None


def ranked(**kw):
    """Faults sorted worst first: reached the limit, then ends wrong, then reached it sooner."""
    rows = []
    for f in FAULTS:
        run = simulate(f, **kw)
        s = metrics(run)
        a = alarm_time(run)
        rows.append(dict(s, fault=f, alarm=a, warned=a is not None and (s["t_limit"] is None or a < s["t_limit"])))
    return sorted(rows, key=lambda r: (r["hit"], round(r["final_err"], 2), -(r["t_limit"] or 1e9)), reverse=True)


if __name__ == "__main__":
    f = lambda x: "never" if x is None else f"{x:.3f}"
    print(f"{'rank':<5}{'fault':<12}{'peak|q|':>8}{'final err':>10}{'limit at':>9}{'alarm at':>9}  warned first")
    for k, r in enumerate(ranked(), 1):
        print(f"{k:<5}{r['fault']:<12}{r['peak']:>8.2f}{r['final_err']:>10.3f}{f(r['t_limit']):>9}{f(r['alarm']):>9}  {r['warned']}")
