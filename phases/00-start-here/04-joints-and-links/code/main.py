# 레슨 00/04: 링크 하나와 두 개의 끝점이 "얼마나 옆으로, 얼마나 위로" 가 되는 위치를 cos 와 sin 으로 계산한다
import math


def hand_position(length, angle):
    """Hand of one link: (how far across, how far up). The angle is in radians, counted from straight across."""
    return length * math.cos(angle), length * math.sin(angle)


def two_link_position(length1, length2, angle1, angle2):
    """Hand of two links. angle2 is measured from the first link, so the second link points at angle1 + angle2."""
    x1, z1 = hand_position(length1, angle1)
    x2, z2 = hand_position(length2, angle1 + angle2)
    return x1 + x2, z1 + z2


if __name__ == "__main__":
    q = math.radians(30)
    print("one link, 30 degrees:", hand_position(0.4, q))
    print("two links, 30 and 60 degrees:", two_link_position(0.4, 0.3, q, math.radians(60)))
