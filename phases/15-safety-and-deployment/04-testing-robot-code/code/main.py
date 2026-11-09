# 레슨 15/04: fake clock, mock joint 과 PD 제어기, 녹화 trace 를 만드는 run 으로 로봇 코드 테스트 도구를 보여 준다
import numpy as np


class FakeClock:
    """Time that moves only when a test says so: no sleeping, no flakiness."""

    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def advance(self, dt):
        self.t += dt


class MockJoint:
    """1-DOF plant that refuses any torque over its limit (NaN included) and records what it accepted."""

    def __init__(self, J=0.5, b=0.2, tau_limit=10.0):
        self.J, self.b, self.tau_limit = J, b, tau_limit
        self.q = self.qd = 0.0
        self.commands = []

    def step(self, tau, dt):
        if not abs(tau) <= self.tau_limit:  # written this way so NaN fails too
            raise ValueError(f"command {tau} is over the limit {self.tau_limit}")
        self.commands.append(tau)
        self.qd += (tau - self.b * self.qd) / self.J * dt
        self.q += self.qd * dt


class Controller:
    """PD with a finite-difference derivative. A long gap between updates or a non-finite input gives zero torque."""

    def __init__(self, clock, kp=40.0, kd=4.0, tau_max=10.0, timeout=0.05, polarity=1):
        self.clock, self.kp, self.kd, self.tau_max = clock, kp, kd, tau_max
        self.timeout, self.polarity = timeout, polarity
        self.last_t = self.last_q = None
        self.stale = False

    def update(self, q_meas, q_ref):
        now, last_t, last_q = self.clock.now(), self.last_t, self.last_q
        self.stale = not (np.isfinite(q_meas) and np.isfinite(q_ref)) or (last_t is not None and now - last_t > self.timeout)
        if np.isfinite(q_meas):
            self.last_t, self.last_q = now, q_meas
        if self.stale:
            return 0.0
        dq = (q_meas - last_q) / (now - last_t) if last_t is not None and now > last_t else 0.0
        tau = self.kp * (q_ref - q_meas) - self.kd * dq
        return self.polarity * float(np.clip(tau, -self.tau_max, self.tau_max))


def run(ctrl, joint, clock, q_ref, T=1.0, dt=0.01):
    """Closed loop on fake time. Returns the trace as rows of (q_meas, q_ref, tau): the thing a replay test stores."""
    rows = []
    for _ in range(int(round(T / dt))):
        clock.advance(dt)
        q_meas = joint.q
        tau = ctrl.update(q_meas, q_ref)
        joint.step(tau, dt)
        rows.append((q_meas, q_ref, tau))
    return rows


if __name__ == "__main__":
    clock = FakeClock()
    rows = run(Controller(clock), MockJoint(), clock, q_ref=1.0, T=3.0)
    print(f"{len(rows)} samples, first torque {rows[0][2]:.2f}, last q {rows[-1][0]:.3f}")
