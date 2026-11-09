# 레슨 00/01: 로봇 데이터용 numpy 가드. shape 검사, 도/라디안 구분, z축 회전
import numpy as np


def check_shape(x, shape, name="array") -> np.ndarray:
    """Return x as a float array if it matches shape; None in shape matches any length."""
    a = np.asarray(x, dtype=float)
    if a.ndim != len(shape) or any(s is not None and s != n for s, n in zip(shape, a.shape)):
        want = ", ".join("N" if s is None else str(s) for s in shape)
        raise ValueError(f"{name}: expected shape ({want}), got {', '.join(map(str, a.shape))}")
    return a


def deg2rad(x):
    return np.asarray(x, dtype=float) * np.pi / 180.0


def rad2deg(x):
    return np.asarray(x, dtype=float) * 180.0 / np.pi


def looks_like_degrees(q, limit: float = 2 * np.pi) -> bool:
    # ponytail: a continuous joint can really pass 2*pi; raise `limit` for those joints
    return bool(np.max(np.abs(np.asarray(q, dtype=float))) > limit)


def joint_angles(q) -> np.ndarray:
    """Joint angles in radians, refusing values that look like degrees."""
    a = check_shape(q, (None,), "q")
    if looks_like_degrees(a):
        raise ValueError(f"q looks like degrees (max |q| = {np.max(np.abs(a)):.1f}); convert with deg2rad")
    return a


def rotate_z(points, theta: float) -> np.ndarray:
    """Rotate N points (N, 3) about z. Points are rows, so the matrix is applied as p @ R.T."""
    p = check_shape(points, (None, 3), "points")
    c, s = np.cos(theta), np.sin(theta)
    R = np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])
    return p @ R.T


if __name__ == "__main__":
    print("cos(90 deg, converted):", np.cos(deg2rad(90.0)))
    print("cos(90 fed as rad):    ", np.cos(90.0))
    print(rotate_z([[1.0, 0.0, 0.0]], np.pi / 2))
