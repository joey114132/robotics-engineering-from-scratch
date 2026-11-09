# 레슨 15/02: 하트비트 watchdog, 정지 거리 v^2/(2a), 토크 차단과 ramp 정지의 비교를 1자유도 관절로 시뮬레이션한다
import numpy as np


class Watchdog:
    """Trips when no heartbeat has arrived for longer than `timeout` seconds."""

    def __init__(self, timeout):
        self.timeout, self.last = timeout, 0.0

    def beat(self, t):
        self.last = t

    def tripped(self, t):
        return t - self.last > self.timeout


def stop_distance(v, a):
    """Constant deceleration a from speed v: v = a t, x = v t - a t^2 / 2 = v^2 / (2 a)."""
    return v * v / (2.0 * a)


def max_timeout(room, v, a):
    """Longest timeout so travel during it (v T) plus braking still fits in `room`."""
    t = (room - stop_distance(v, a)) / v
    if t <= 0:
        raise ValueError(f"braking alone needs {stop_distance(v, a):.3f} but only {room:.3f} is free")
    return t


def simulate(stop="ramp", timeout=0.05, v0=2.0, a=8.0, q_lim=1.5, t_loss=0.5, T=12.0, dt=1e-3, hb=0.01,
             J=0.5, b=0.2, kv=20.0):
    """Joint at speed v0 follows a velocity command. Commands (and heartbeats) stop at t_loss; the last one stays latched."""
    wd, q, v, trip, hit = Watchdog(timeout), 0.0, v0, None, False
    rows = []
    log = dict(v_loss=None, q_loss=None, q_trip=None, v_trip=None, t_stop=None)
    for i in range(int(round(T / dt))):
        t = i * dt
        if t < t_loss and i % round(hb / dt) == 0:
            wd.beat(t)
        if log["v_loss"] is None and t >= t_loss:
            log["v_loss"], log["q_loss"] = v, q
        if trip is None and wd.tripped(t):
            trip, log["q_trip"], log["v_trip"] = t, q, v
        if trip is None:
            tau = kv * (v0 - v)  # stale command keeps being executed
        elif stop == "cut":
            tau = 0.0  # no brake modelled: only friction slows the joint
        else:
            tau = -np.sign(v) * min(J * a, J * abs(v) / dt)  # velocity ramps to zero, never reverses
        v += (tau - b * v) / J * dt
        q += v * dt
        if q >= q_lim:
            q, v, hit = q_lim, 0.0, True  # hard stop
        rows.append((t, q, v))
        if trip is not None and log["t_stop"] is None and abs(v) < 1e-3:
            log["t_stop"] = t
    return dict(log, trace=np.array(rows), hit=hit, q_final=q, stop_dist=q - log["q_trip"], overrun=q - log["q_loss"],
                stop_time=None if log["t_stop"] is None else log["t_stop"] - trip)


if __name__ == "__main__":
    print(f"max timeout for 0.5 rad of room at 2 rad/s, a=8: {max_timeout(0.5, 2.0, 8.0):.3f} s")
    for mode in ("cut", "ramp"):
        r = simulate(mode, q_lim=100.0)
        print(f"{mode:<5} stop distance {r['stop_dist']:.2f} rad, time to rest {r['stop_time']}, hits 1.5 rad limit: {simulate(mode)['hit']}")
