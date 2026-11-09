# 레슨 02/03: 평면 2링크 팔의 Jacobian 을 해석적으로, 유한 차분으로 만들고 속도와 힘을 사상한다
import numpy as np


def fk(q, L):
    (l1, l2), (q1, q2) = L, q
    return np.array([l1 * np.cos(q1) + l2 * np.cos(q1 + q2), l1 * np.sin(q1) + l2 * np.sin(q1 + q2)])


def jacobian(q, L):
    """Analytic J = d(tip)/d(q). Column j is the tip velocity per unit speed of joint j."""
    (l1, l2), (q1, q2) = L, q
    s1, c1, s12, c12 = np.sin(q1), np.cos(q1), np.sin(q1 + q2), np.cos(q1 + q2)
    return np.array([[-l1 * s1 - l2 * s12, -l2 * s12], [l1 * c1 + l2 * c12, l2 * c12]])


def jacobian_fd(q, L, eps=1e-6):
    """Central difference: nudge each joint by +-eps and watch the tip move."""
    q = np.asarray(q, float)
    cols = []
    for j in range(len(q)):
        dq = np.zeros_like(q)
        dq[j] = eps
        cols.append((fk(q + dq, L) - fk(q - dq, L)) / (2 * eps))
    return np.column_stack(cols)


def J_times(J, qd):
    """Tip velocity for joint speeds qd."""
    return J @ np.asarray(qd, float)


def joint_torque(J, F):
    """Static joint torque that balances a tip force F: tau = J^T F."""
    return J.T @ np.asarray(F, float)


if __name__ == "__main__":
    L, q = (0.5, 0.4), np.array([0.3, 0.8])
    Ja, Jn = jacobian(q, L), jacobian_fd(q, L)
    print("max |analytic - fd| =", np.abs(Ja - Jn).max())
    print("tip velocity for qd = (0.5, -0.2):", J_times(Ja, [0.5, -0.2]))
    print("torque to push the tip with (0, -10) N:", joint_torque(Ja, [0.0, -10.0]))
