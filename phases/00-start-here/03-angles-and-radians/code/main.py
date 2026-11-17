# 레슨 00/03: 각도를 도와 라디안으로 바꾸고, 큰 각도를 한 바퀴 안으로 감는다
import math

FULL_TURN = 2 * math.pi         # 360 degrees is about 6.28 radians
QUARTER_TURN = FULL_TURN / 4    # 90 degrees is about 1.57 radians


def deg_to_rad(degrees):
    return degrees * math.pi / 180


def rad_to_deg(radians):
    return radians * 180 / math.pi


def wrap_turn(angle):
    """Bring any angle (radians) back into one turn, 0 up to (not including) a full turn."""
    return angle % FULL_TURN    # 450 degrees points the same way as 90 degrees


if __name__ == "__main__":
    for d in (90, 180, 360):
        print(f"{d} degrees = {deg_to_rad(d):.2f} radians")
    print(f"450 degrees wraps to {rad_to_deg(wrap_turn(deg_to_rad(450))):.0f} degrees")
    print(f"-90 degrees wraps to {rad_to_deg(wrap_turn(deg_to_rad(-90))):.0f} degrees")
