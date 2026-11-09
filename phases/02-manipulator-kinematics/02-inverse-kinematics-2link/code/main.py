# 레슨 02/02: 평면 2링크 팔의 해석적 inverse kinematics (elbow-up, elbow-down)와 FK 로 되짚어 확인
import numpy as np


def fk(q, L):
    """Tip position of a planar two-link arm. Joint angles are measured counter-clockwise."""
    (l1, l2), (q1, q2) = L, q
    return np.array([l1 * np.cos(q1) + l2 * np.cos(q1 + q2), l1 * np.sin(q1) + l2 * np.sin(q1 + q2)])


def ik(p, L, elbow="down", tol=1e-9):
    """Return (q1, q2) for tip target p. 'down' means q2 >= 0. Raises ValueError if p is out of reach."""
    (l1, l2), (x, y) = L, p
    c2 = (x * x + y * y - l1 * l1 - l2 * l2) / (2 * l1 * l2)  # law of cosines
    if abs(c2) > 1 + tol:
        raise ValueError(f"unreachable: |p| = {np.hypot(x, y):.4f} m, reachable band is {abs(l1 - l2):.4f} to {l1 + l2:.4f} m")
    c2 = np.clip(c2, -1.0, 1.0)  # rounding noise at the boundary is not a refusal
    s2 = np.sqrt(1 - c2 * c2) * (1 if elbow == "down" else -1)
    q2 = np.arctan2(s2, c2)
    q1 = np.arctan2(y, x) - np.arctan2(l2 * s2, l1 + l2 * c2)
    return np.array([q1, q2])


if __name__ == "__main__":
    L, p = (0.5, 0.4), (0.6, 0.3)
    for e in ("down", "up"):
        q = ik(p, L, e)
        print(e, np.round(q, 4), "fk check", np.round(fk(q, L), 6))
    try:
        ik((1.0, 0.0), L)
    except ValueError as err:
        print(err)
