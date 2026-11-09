# 레슨 01/01: 회전행렬과 SE(3) 합성·역변환을 numpy 로 직접 만든다
import numpy as np


def rot_x(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rot_y(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rot_z(a: float) -> np.ndarray:
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def is_rotation(R: np.ndarray, tol: float = 1e-9) -> bool:
    """Orthonormal columns and determinant +1."""
    return bool(np.allclose(R.T @ R, np.eye(3), atol=tol) and np.isclose(np.linalg.det(R), 1.0, atol=tol))


def reorthonormalize(R: np.ndarray) -> np.ndarray:
    """Closest rotation to R (SVD polar factor), used to repair accumulated drift."""
    U, _, Vt = np.linalg.svd(R)
    return U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt


def make_T(R: np.ndarray, p) -> np.ndarray:
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = p
    return T


def invert_T(T: np.ndarray) -> np.ndarray:
    """Closed form [R^T, -R^T p]; no general matrix inverse needed."""
    R, p = T[:3, :3], T[:3, 3]
    return make_T(R.T, -R.T @ p)


def transform_point(T: np.ndarray, point) -> np.ndarray:
    return T[:3, :3] @ np.asarray(point, dtype=float) + T[:3, 3]


if __name__ == "__main__":
    T = make_T(rot_z(np.pi / 2), [1, 2, 3])
    print("point (1,0,0) ->", transform_point(T, [1, 0, 0]))
    print("T^-1 T == I:", np.allclose(invert_T(T) @ T, np.eye(4)))
