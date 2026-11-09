# 레슨 01/02: 평면 2R/3R 과 SE(3) 곱으로 만든 회전관절 사슬의 순기구학
import numpy as np


def fk_planar(lengths, angles):
    """Tip (x, y) and heading of a planar chain; each angle is relative to the previous link."""
    heading = np.cumsum(angles)
    x = float(np.sum(np.asarray(lengths) * np.cos(heading)))
    y = float(np.sum(np.asarray(lengths) * np.sin(heading)))
    return x, y, float(heading[-1])


def _rz(q):
    c, s = np.cos(q), np.sin(q)
    T = np.eye(4)
    T[:2, :2] = [[c, -s], [s, c]]
    return T


def _tx(l):
    T = np.eye(4)
    T[0, 3] = l
    return T


def fk_chain(angles, lengths) -> np.ndarray:
    """Product of Rz(q_i) @ Tx(l_i): rotate about the joint axis, then walk along the link."""
    T = np.eye(4)
    for q, l in zip(angles, lengths):
        T = T @ _rz(q) @ _tx(l)
    return T


def reach_bounds(lengths):
    """Min and max distance of the tip from the base for a planar chain with free joints."""
    hi = float(sum(lengths))
    lo = max(0.0, 2 * max(lengths) - hi)
    return lo, hi


if __name__ == "__main__":
    print(fk_planar([1.0, 0.5], [np.pi / 2, -np.pi / 2]))
    print(reach_bounds([3.0, 1.0]))
