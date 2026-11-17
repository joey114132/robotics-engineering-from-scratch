# 레슨 00/02: 점은 숫자 한 쌍(또는 세 개)이다. 점 옮기기, 원점 바꾸기, 두 점 사이 거리, 경로 길이
import math

ROUTE = [(0, 0), (2, 0), (2, 1.5)]   # three marked spots on the floor, in metres from the corner of the room


def shift(point, move):
    return tuple(c + d for c, d in zip(point, move))        # add the move to every number


def measured_from(point, origin):
    return tuple(c - o for c, o in zip(point, origin))      # the same spot, counted from a new corner


def distance(p, q):
    return math.hypot(*(b - a for a, b in zip(p, q)))       # how far across, how far up, then the diagonal


def path_length(points):
    return sum(distance(a, b) for a, b in zip(points, points[1:]))


def lerp(p, q, t):
    return tuple(a + (b - a) * t for a, b in zip(p, q))     # the spot a fraction t of the way from p to q


if __name__ == "__main__":
    print("A to B:", distance(ROUTE[0], ROUTE[1]), "B to C:", distance(ROUTE[1], ROUTE[2]))
    print("drive via B:", path_length(ROUTE), " straight A to C:", distance(ROUTE[0], ROUTE[2]))
    print("B counted from A's corner vs from C:", measured_from(ROUTE[1], ROUTE[0]), measured_from(ROUTE[1], ROUTE[2]))
