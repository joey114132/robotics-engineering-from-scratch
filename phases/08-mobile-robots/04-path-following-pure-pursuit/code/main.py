# 레슨 08/04: 차동 구동 모델 위의 pure pursuit, lookahead 거리가 코너 절단과 진동에 미치는 영향
import numpy as np


def dense(corners, step=0.02):
    """Sample a polyline every `step` metres."""
    c = np.asarray(corners, float)
    return np.vstack([a + (b - a) * np.linspace(0, 1, max(int(np.linalg.norm(b - a) / step), 2), endpoint=False)[:, None] for a, b in zip(c[:-1], c[1:])] + [c[-1:]])


def lookahead_point(path, pos, ld):
    """First path point at least `ld` away from the robot, searching ahead of the closest point."""
    i = np.linalg.norm(path - pos, axis=1).argmin()
    far = np.nonzero(np.linalg.norm(path[i:] - pos, axis=1) >= ld)[0]
    return path[i + far[0]] if len(far) else path[-1]


def curvature(pose, target):
    """Circle through the robot (tangent to its heading) and the target: k = 2 y / d^2, y = lateral offset."""
    dx, dy = target - pose[:2]
    y = -np.sin(pose[2]) * dx + np.cos(pose[2]) * dy
    return 2 * y / (dx * dx + dy * dy)


def follow(corners, ld, v=1.0, start=(0.0, 0.6, 0.0), tau=0.4, dt=0.02, t_max=60.0):
    """Drive the path. Turn rate follows the command through a first-order lag tau (a real drive cannot turn instantly)."""
    path, pose, w = dense(corners), np.array(start, float), 0.0
    traj = [pose.copy()]
    for _ in range(int(t_max / dt)):
        w += (v * curvature(pose, lookahead_point(path, pose[:2], ld)) - w) * (1 - np.exp(-dt / tau))  # exact lag step
        pose = pose + dt * np.array([v * np.cos(pose[2]), v * np.sin(pose[2]), w])
        traj.append(pose.copy())
        if np.linalg.norm(pose[:2] - path[-1]) < 0.15:
            break
    return np.array(traj)


def cross_track(traj, path):
    """Distance from every trajectory point to the nearest path sample."""
    return np.linalg.norm(traj[:, None, :2] - path[None], axis=2).min(axis=1)


def sign_changes(x, dead=0.02):
    s = np.sign(x[np.abs(x) > dead])
    return int((s[1:] != s[:-1]).sum())


if __name__ == "__main__":
    corners = [(0, 0), (10, 0), (10, 10)]
    for ld in (0.4, 1.5, 4.0):
        t = follow(corners, ld)
        leg = t[t[:, 0] < 8]
        print(f"ld {ld}: corner cut {np.linalg.norm(t[:, :2] - [10, 0], axis=1).min():.2f} m, sign changes on leg 1: {sign_changes(leg[:, 1])}, max |y| after start {np.abs(leg[len(leg)//4:, 1]).max():.2f}")
