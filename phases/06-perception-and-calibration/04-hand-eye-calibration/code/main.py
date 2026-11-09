# 레슨 06/04: AX = XB 손-눈 보정. 회전축을 맞춰 R_X 를 먼저 풀고, 이동은 선형 최소제곱으로 푼다
import numpy as np


def rodrigues(w):
    th = np.linalg.norm(w)
    if th < 1e-12:
        return np.eye(3)
    k = w / th
    Kx = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * Kx + (1 - np.cos(th)) * Kx @ Kx


def log_rot(R):
    """Rotation vector (axis * angle) of R, for angles below pi."""
    th = np.arccos(np.clip((np.trace(R) - 1) / 2, -1, 1))
    if th < 1e-12:
        return np.zeros(3)
    return th / (2 * np.sin(th)) * np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])


def make_T(R, p):
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, p
    return T


def make_motions(X, n, spread_deg, rot_noise_deg=0.0, t_noise=0.0, seed=0):
    """n gripper motions A whose rotation axes lie within spread_deg of z, and camera motions B = X^-1 A X plus noise."""
    rng, As, Bs = np.random.default_rng(seed), [], []
    for _ in range(n):
        psi, phi = np.radians(spread_deg) * rng.random(), 2 * np.pi * rng.random()
        axis = np.array([np.sin(psi) * np.cos(phi), np.sin(psi) * np.sin(phi), np.cos(psi)])
        A = make_T(rodrigues(axis * rng.choice([-1, 1]) * rng.uniform(0.3, 0.8)), rng.uniform(-0.15, 0.15, 3))
        E = make_T(rodrigues(np.radians(rot_noise_deg) * rng.normal(size=3)), t_noise * rng.normal(size=3))
        As.append(A)
        Bs.append(np.linalg.inv(X) @ A @ X @ E)
    return As, Bs


def solve_hand_eye(As, Bs):
    """Rotation: log(R_A) = R_X log(R_B), aligned by SVD (Kabsch). Translation: (R_A - I) t_X = R_X t_B - t_A.
    Returns X and the singular values of the axis correlation matrix (the observability check)."""
    if len(As) < 2:
        raise ValueError("need at least 2 motions")
    alpha = np.array([log_rot(A[:3, :3]) for A in As])
    beta = np.array([log_rot(B[:3, :3]) for B in Bs])
    U, s, Vt = np.linalg.svd(alpha.T @ beta)
    R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
    M = np.vstack([A[:3, :3] - np.eye(3) for A in As])
    y = np.concatenate([R @ B[:3, 3] - A[:3, 3] for A, B in zip(As, Bs)])
    return make_T(R, np.linalg.lstsq(M, y, rcond=None)[0]), s


def pose_error(Xe, X):
    """(rotation error in degrees, translation error in metres)."""
    ang = np.degrees(np.linalg.norm(log_rot(Xe[:3, :3] @ X[:3, :3].T)))
    return float(ang), float(np.linalg.norm(Xe[:3, 3] - X[:3, 3]))


if __name__ == "__main__":
    X = make_T(rodrigues(np.array([0.3, -0.5, 0.8])), [0.05, 0.03, 0.08])
    for spread in (0.0, 15.0, 60.0):
        Xe, _ = solve_hand_eye(*make_motions(X, 12, spread, 0.2, 0.001, seed=1))
        print(f"axis spread {spread:4.0f} deg  rotation err {pose_error(Xe, X)[0]:6.2f} deg  translation err {pose_error(Xe, X)[1] * 1000:6.1f} mm")
