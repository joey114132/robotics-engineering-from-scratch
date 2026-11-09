# 레슨 02/04: 2링크 팔의 singularity 에서 역 Jacobian 속도가 폭주하는 것과 damped least squares 로 막는 것
import numpy as np


def jacobian(q, L):
    (l1, l2), (q1, q2) = L, q
    s1, c1, s12, c12 = np.sin(q1), np.cos(q1), np.sin(q1 + q2), np.cos(q1 + q2)
    return np.array([[-l1 * s1 - l2 * s12, -l2 * s12], [l1 * c1 + l2 * c12, l2 * c12]])


def manipulability(J):
    """sqrt(det(J J^T)): equals |det J| for a square J and falls to 0 at a singularity."""
    return float(np.sqrt(max(np.linalg.det(J @ J.T), 0.0)))


def solve(J, v, lam):
    """Joint speeds for tip velocity v. lam = 0 is the plain inverse. lam > 0 is damped least squares."""
    J, v = np.asarray(J, float), np.asarray(v, float)
    if lam == 0.0:
        return np.linalg.solve(J, v)
    return J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(len(v)), v)  # speed <= |v| / (2 lam)


if __name__ == "__main__":
    L, v = (0.5, 0.4), np.array([0.1, 0.0])
    for q2 in (0.5, 0.1, 0.02, 0.005):
        J = jacobian([0.0, q2], L)
        print(f"q2={q2:5.3f}  det={np.linalg.det(J):.5f}  plain |qd|={np.linalg.norm(solve(J, v, 0)):7.2f}"
              f"  damped |qd|={np.linalg.norm(solve(J, v, 0.05)):5.2f}")
