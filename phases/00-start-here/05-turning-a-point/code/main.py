# 레슨 00/05: 점을 원점 둘레로 돌리는 두 방법. 식으로 직접 계산하기와 2x2 숫자 표(회전 행렬)에 @ 로 곱하기
import math

import numpy as np


def rotate(point, angle):
    """Turn (across, up) around the origin by angle (radians, counter-clockwise)."""
    x, y = point
    c, s = math.cos(angle), math.sin(angle)
    return x * c - y * s, x * s + y * c


def rotation_table(angle):
    """The same recipe as a 2x2 table of numbers (a rotation matrix)."""
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s], [s, c]])


def rotate_with_table(point, angle):
    return tuple(rotation_table(angle) @ np.asarray(point, dtype=float))


if __name__ == "__main__":
    q = math.radians(90)
    print("plain math:", rotate((1.0, 0.0), q))
    print("table @ point:", rotate_with_table((1.0, 0.0), q))
