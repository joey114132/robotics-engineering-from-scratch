# 레슨 14/02: 통신 그래프 위의 평균 합의, Laplacian 두 번째 고유값이 수렴 속도를 정한다
import numpy as np


def ring(n) -> np.ndarray:
    A = np.zeros((n, n))
    for i in range(n):
        A[i, (i + 1) % n] = A[(i + 1) % n, i] = 1
    return A


def complete(n) -> np.ndarray:
    return np.ones((n, n)) - np.eye(n)


def laplacian(A) -> np.ndarray:
    """L = D - A. Row sums are zero, so the all-ones vector is an eigenvector with eigenvalue 0."""
    return np.diag(A.sum(axis=1)) - A


def lambda2(L) -> float:
    """Second-smallest eigenvalue (algebraic connectivity): > 0 exactly when the graph is connected."""
    return float(np.linalg.eigvalsh(L)[1])


def run(x0, A, eps, steps) -> np.ndarray:
    """x_i += eps * sum_j A_ij (x_j - x_i), i.e. x <- (I - eps L) x. Returns (steps + 1, n)."""
    M = np.eye(len(A)) - eps * laplacian(A)
    out = [np.asarray(x0, float)]
    for _ in range(steps):
        out.append(M @ out[-1])
    return np.array(out)


def steps_to_agree(x0, A, eps, tol=1e-3, limit=100000) -> int:
    M, x = np.eye(len(A)) - eps * laplacian(A), np.asarray(x0, float)
    for k in range(limit):
        if np.ptp(x) < tol:
            return k
        x = M @ x
    return limit


if __name__ == "__main__":
    x0 = np.array([4.0, -1.0, 2.0, 7.0, 0.0, 3.0, -5.0, 1.0])
    for name, A in (("ring", ring(8)), ("complete", complete(8))):
        print(name, round(lambda2(laplacian(A)), 3), steps_to_agree(x0, A, 0.05))
