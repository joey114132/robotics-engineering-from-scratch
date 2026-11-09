# 레슨 13/04: 학습 정책을 감싸는 결정적 안전 래퍼(clip, 변화율 제한, 오래된 관측 hold, fallback, 개입 로그)와 시뮬레이션
import collections

import numpy as np

DT = 0.05


class Wrapper:
    """Deterministic layer between a non-deterministic policy and the actuator. Same inputs always give the same output."""

    def __init__(self, lo, hi, max_step, max_age, deadline, fallback=0.0):
        self.lo, self.hi, self.max_step, self.max_age, self.deadline, self.fallback = lo, hi, max_step, max_age, deadline, fallback
        self.last_out, self.last_good, self.log = 0.0, 0, []

    def act(self, t, obs, stamp, policy):
        """obs is None when missing; stamp is the time the observation was taken. policy(obs) is only called on a usable one."""
        raw, kind = None, None
        if obs is not None and t - stamp <= self.max_age:
            self.last_good = t
            raw = policy(obs)
            if not np.isfinite(raw):
                target, kind = self.fallback, "nonfinite"
            else:
                target = float(np.clip(raw, self.lo, self.hi))
                kind = "clip" if target != raw else None
        elif t - self.last_good > self.deadline:
            target, kind = self.fallback, "fallback"
        else:
            target, kind = self.last_out, "hold"
        out = float(np.clip(target, self.last_out - self.max_step, self.last_out + self.max_step))
        if out != target and kind is None:
            kind = "rate"
        if kind:
            self.log.append(dict(t=t, kind=kind, raw=raw, out=out))
        self.last_out = out
        return out


def flaky_policy(t):
    """A learned-policy stand-in: good feedback law, plus a flipped-sign burst and one NaN."""
    return lambda x: 8.0 if 20 <= t < 28 else float("nan") if t == 45 else -2.0 * x


def simulate(wrapped, T=140):
    """Point at x=1 should go to 0. Observation drops out for ticks 70-84 (15 ticks, longer than the deadline)."""
    w = Wrapper(lo=-1.0, hi=1.0, max_step=0.2, max_age=1, deadline=10)
    x, seen, xs, raws, outs = 1.0, 1.0, [1.0], [], []
    for t in range(T):
        dropped = 70 <= t < 85
        if not dropped:
            seen = x
        pol = flaky_policy(t)
        raw = pol(seen)
        if wrapped:
            u = w.act(t, None if dropped else x, None if dropped else t, pol)
        else:
            u = raw if np.isfinite(raw) else 0.0  # a bare actuator saturates at +-10 and ignores NaN
            u = float(np.clip(u, -10, 10))
        x += DT * u
        xs.append(x), raws.append(raw), outs.append(u)
    return dict(x=np.array(xs), raw=np.array(raws), out=np.array(outs), log=w.log, counts=collections.Counter(e["kind"] for e in w.log))


if __name__ == "__main__":
    for flag in (False, True):
        r = simulate(flag)
        print(flag, "max|x|", round(np.abs(r["x"]).max(), 2), "final", round(r["x"][-1], 3), dict(r["counts"]))
