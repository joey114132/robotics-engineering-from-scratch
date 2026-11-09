# 레슨 08/01: 차동 구동 운동학, 바퀴 속도 dead reckoning, 반지름과 윤거 오차가 만드는 경로 어긋남
import numpy as np


def wheels_to_twist(wl, wr, r, b):
    """Wheel angular speeds (rad/s) to forward speed v (m/s) and turn rate w (rad/s). r = wheel radius, b = track width."""
    return r * (wr + wl) / 2, r * (wr - wl) / b


def twist_to_wheels(v, w, r, b):
    return (v - w * b / 2) / r, (v + w * b / 2) / r


def dead_reckon(wl, wr, dt, r, b, pose0=(0.0, 0.0, 0.0)):
    """Integrate wheel speeds into poses (x, y, heading). Each step is an exact circular arc."""
    v, w = wheels_to_twist(np.asarray(wl, float), np.asarray(wr, float), r, b)
    dth = w * dt
    step = v * dt * np.sinc(dth / (2 * np.pi))  # chord length of the arc
    th = pose0[2] + np.cumsum(dth) - dth / 2     # heading at the middle of each step
    xy = np.array(pose0[:2]) + np.cumsum(np.stack([step * np.cos(th), step * np.sin(th)], 1), axis=0)
    return np.vstack([pose0, np.column_stack([xy, pose0[2] + np.cumsum(dth)])])


def square_wheels(side, v, dt, r, b, n_turn=157):
    """Wheel commands that drive a square of `side` metres, planned with the nominal r and b."""
    n_side = round(side / v / dt)
    w_turn = (np.pi / 2) / (n_turn * dt)
    cmd = [(v, 0.0)] * n_side + [(0.0, w_turn)] * n_turn
    wl, wr = zip(*[twist_to_wheels(v_, w_, r, b) for v_, w_ in cmd * 4])
    return np.array(wl), np.array(wr)


def closure_error(wl, wr, dt, r, b):
    """Distance between where a closed loop should end (the start) and where these r, b put the robot."""
    return float(np.linalg.norm(dead_reckon(wl, wr, dt, r, b)[-1, :2]))


if __name__ == "__main__":
    R, B, DT = 0.05, 0.30, 0.01
    wl, wr = square_wheels(2.0, 0.5, DT, R, B)
    for name, r, b in (("nominal", R, B), ("track +1%", R, B * 1.01), ("radius +1%", R * 1.01, B)):
        print(f"{name:10s} closure error {closure_error(wl, wr, DT, r, b):.3f} m")
