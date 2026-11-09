# 레슨 01/03: Rodrigues 회전, 단위 quaternion, 부호 보정을 넣은 slerp 를 numpy 로 직접 만든다
import numpy as np


def _unit(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)


def rodrigues(axis, angle):
    k = _unit(axis)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * K @ K


def quat_from_axis_angle(axis, angle):
    """Unit quaternion (w, x, y, z)."""
    return np.concatenate([[np.cos(angle / 2)], np.sin(angle / 2) * _unit(axis)])


def quat_mul(a, b):
    return np.concatenate([[a[0] * b[0] - a[1:] @ b[1:]], a[0] * b[1:] + b[0] * a[1:] + np.cross(a[1:], b[1:])])


def quat_to_R(q):
    w, x, y, z = _unit(q)
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def R_to_quat(R):
    """Shepperd's method: pick the largest of w, x, y, z so the square root stays well conditioned."""
    if np.trace(R) > 0:
        s = 2 * np.sqrt(np.trace(R) + 1)
        return np.array([s / 4, (R[2, 1] - R[1, 2]) / s, (R[0, 2] - R[2, 0]) / s, (R[1, 0] - R[0, 1]) / s])
    i = int(np.argmax(np.diag(R)))
    j, k = (i + 1) % 3, (i + 2) % 3
    s = 2 * np.sqrt(1 + R[i, i] - R[j, j] - R[k, k])
    q = np.zeros(4)
    q[0], q[1 + i], q[1 + j], q[1 + k] = (R[k, j] - R[j, k]) / s, s / 4, (R[j, i] + R[i, j]) / s, (R[k, i] + R[i, k]) / s
    return q


def slerp(q0, q1, t, fix=True):
    """Great-circle interpolation. fix=True negates q1 when dot < 0 so the short arc is taken."""
    d = float(q0 @ q1)
    if fix and d < 0:
        q1, d = -q1, -d
    om = np.arccos(min(d, 1.0))
    if om < 1e-9:
        return q0
    return (np.sin((1 - t) * om) * q0 + np.sin(t * om) * q1) / np.sin(om)


def path_angle(q0, q1, fix=True, n=400):
    """Total rotation angle (rad) swept by the slerp path, summed over small steps."""
    qs = [slerp(q0, q1, t, fix) for t in np.linspace(0, 1, n)]
    return float(sum(2 * np.arccos(min(1.0, a @ b)) for a, b in zip(qs, qs[1:])))


if __name__ == "__main__":
    q0, q1 = quat_from_axis_angle([0, 0, 1], 0.0), -quat_from_axis_angle([0, 0, 1], 0.1)
    print("swept without fix:", round(path_angle(q0, q1, fix=False), 3), "rad")
    print("swept with fix:   ", round(path_angle(q0, q1, fix=True), 3), "rad")
