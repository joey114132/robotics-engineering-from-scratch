# 레슨 05/06: 시각이 붙은 pose buffer. 두 sample 사이는 lerp/slerp 로 보간하고 범위 밖은 추측하지 않고 거부한다
import bisect

import numpy as np


def quat_to_R(q):
    w, x, y, z = q / np.linalg.norm(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def slerp(q0, q1, t):
    """Great-circle interpolation along the short arc. t outside 0..1 continues the same turn rate."""
    d = float(q0 @ q1)
    if d < 0:
        q1, d = -q1, -d
    om = np.arccos(min(d, 1.0))
    if om < 1e-9:
        return q0
    return (np.sin((1 - t) * om) * q0 + np.sin(t * om) * q1) / np.sin(om)


class PoseBuffer:
    """Poses of one frame over time, as (stamp, position, unit quaternion w x y z)."""

    def __init__(self, max_extrapolation=0.0, window=10.0):
        self.t, self.p, self.q = [], [], []
        self.max_extrapolation, self.window = max_extrapolation, window

    def add(self, t, p, q):
        i = bisect.bisect_left(self.t, t)
        if i < len(self.t) and self.t[i] == t:  # same stamp again: keep the newest report
            del self.t[i], self.p[i], self.q[i]
        self.t.insert(i, t), self.p.insert(i, np.asarray(p, float).copy()), self.q.insert(i, np.asarray(q, float).copy())
        while self.t[-1] - self.t[0] > self.window:  # forget history older than the window
            del self.t[0], self.p[0], self.q[0]

    def lookup(self, t):
        """Pose at time t. Raises LookupError if t is outside the stored range plus the allowed extrapolation."""
        if not self.t:
            raise LookupError("empty buffer")
        if t < self.t[0]:
            raise LookupError(f"t={t:.3f} is {self.t[0] - t:.3f} s older than the oldest sample")
        if t > self.t[-1] + self.max_extrapolation + 1e-12:
            raise LookupError(f"t={t:.3f} is {t - self.t[-1]:.3f} s newer than the newest sample")
        if len(self.t) == 1:
            return self.p[0].copy(), self.q[0].copy()
        i = min(bisect.bisect_right(self.t, t) - 1, len(self.t) - 2)
        a = (t - self.t[i]) / (self.t[i + 1] - self.t[i])  # a > 1 only when extrapolating
        return (1 - a) * self.p[i] + a * self.p[i + 1], slerp(self.q[i], self.q[i + 1], a).copy()


def to_world(buf, stamps, points, use_stamps=True):
    """Place sensor-frame points in the world. Each point uses the pose at its own stamp, or the newest pose if use_stamps is False."""
    out = []
    for t, pt in zip(stamps, points):
        p, q = buf.lookup(t if use_stamps else buf.t[-1])
        out.append(quat_to_R(q) @ pt + p)
    return np.array(out)


if __name__ == "__main__":
    buf = PoseBuffer()
    for t in (0.0, 1.0):
        buf.add(t, [2 * t, 0, 0], [np.cos(t / 2), 0, 0, np.sin(t / 2)])
    print("midpoint:", buf.lookup(0.5)[0])
    try:
        buf.lookup(1.2)
    except LookupError as e:
        print("refused:", e)
