# 레슨 01/05: ZYX Euler 각도와 회전행렬 변환, gimbal lock 에서 각속도 사상이 rank 를 잃는 것
import numpy as np


def _rot(axis, a):
    c, s = np.cos(a), np.sin(a)
    i, j = [(1, 2), (2, 0), (0, 1)][axis]
    R = np.eye(3)
    R[i, i], R[i, j], R[j, i], R[j, j] = c, -s, s, c
    return R


def euler_to_R(roll, pitch, yaw):
    """ZYX order: R = Rz(yaw) Ry(pitch) Rx(roll). Roll is applied first, about the x axis."""
    return _rot(2, yaw) @ _rot(1, pitch) @ _rot(0, roll)


def R_to_euler(R, tol=1e-9):
    """(roll, pitch, yaw, locked) with pitch in [-90, 90] deg. At +-90 deg only one angle is defined, so roll is set to 0."""
    pitch = np.arcsin(np.clip(-R[2, 0], -1, 1))
    if abs(R[2, 0]) > 1 - tol:
        return 0.0, pitch, np.arctan2(-R[0, 1], R[1, 1]), True
    return np.arctan2(R[2, 1], R[2, 2]), pitch, np.arctan2(R[1, 0], R[0, 0]), False


def other_spelling(roll, pitch, yaw):
    """The same rotation written with pitch outside [-90, 90] deg: roll and yaw are each 180 deg away."""
    return roll + np.pi, np.pi - pitch, yaw + np.pi


def rate_map(pitch, yaw):
    """E in omega_world = E @ [roll_rate, pitch_rate, yaw_rate]. det E = cos(pitch)."""
    cy, sy, cp, sp = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch)
    return np.array([[cy * cp, -sy, 0], [sy * cp, cy, 0], [-sp, 0, 1]])


def euler_rates(omega, pitch, yaw):
    """Euler angle rates that produce a world angular velocity. Refuses at gimbal lock."""
    E = rate_map(pitch, yaw)
    if abs(np.linalg.det(E)) < 1e-9:
        raise ValueError("gimbal lock: no Euler rates produce this angular velocity")
    return np.linalg.solve(E, np.asarray(omega, float))


if __name__ == "__main__":
    D = np.pi / 180
    for p in (60, 85, 89.9):
        print(p, "deg: det E =", round(np.linalg.det(rate_map(p * D, 0)), 5), " |rates| =", np.linalg.norm(euler_rates([1, 0, 0], p * D, 0)).round(1))
    r, p, y, locked = R_to_euler(euler_to_R(0.4, 90 * D, 0.9))
    print("locked:", locked, "roll reported:", r, "yaw reported:", round(y, 3))
