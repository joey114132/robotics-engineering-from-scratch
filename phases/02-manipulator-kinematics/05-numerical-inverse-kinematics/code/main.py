# 레슨 02/05: 평면 3링크 팔의 damped Newton IK, 관절 한계 clamp, 무작위 재시작
import numpy as np


def fk(q, L):
    """Tip position of a planar arm. Joint angles are relative, counter-clockwise."""
    a = np.cumsum(q)
    return np.array([np.dot(L, np.cos(a)), np.dot(L, np.sin(a))])


def jacobian(q, L):
    """2 x n. Joint j turns every link from j outward, so column j sums those links."""
    a, L = np.cumsum(q), np.asarray(L, float)
    sx, sy = -L * np.sin(a), L * np.cos(a)
    return np.array([np.cumsum(sx[::-1])[::-1], np.cumsum(sy[::-1])[::-1]])


def solve_ik(target, L, q0, lo, hi, lam=0.05, iters=300, tol=1e-6, max_step=0.3):
    """Damped Newton: dq = J^T (J J^T + lam^2 I)^-1 e, clamped to the limits. Returns (q, converged)."""
    target, q = np.asarray(target, float), np.clip(q0, lo, hi).astype(float)
    best_q, best_error = q.copy(), np.inf
    for i in range(iters + 1):
        e = target - fk(q, L)
        error = np.linalg.norm(e)
        if error < best_error:
            best_q, best_error = q.copy(), error
        if error < tol:
            return q, True
        if i == iters:
            break
        J = jacobian(q, L)
        dq = J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(2), e)
        q = np.clip(q + dq * min(1.0, max_step / np.abs(dq).max()), lo, hi)  # cap the biggest joint step
    return best_q, False


def ik_restarts(target, L, lo, hi, n=20, seed=0):
    """Run from n random seeds inside the limits. Returns [(q, converged)], one per seed."""
    rng = np.random.default_rng(seed)
    return [solve_ik(target, L, rng.uniform(lo, hi), lo, hi) for _ in range(n)]


if __name__ == "__main__":
    L, lo, hi = (0.4, 0.3, 0.2), np.array([-np.pi, -2.5, -2.5]), np.array([np.pi, 2.5, 2.5])
    sols = ik_restarts([0.5, 0.3], L, lo, hi)
    print("converged:", sum(ok for _, ok in sols), "of", len(sols), " elbow signs:", sorted({int(np.sign(q[1])) for q, ok in sols if ok}))
    print("unreachable:", solve_ik([1.5, 0.0], L, [0.3, 0.3, 0.3], lo, hi)[1])
