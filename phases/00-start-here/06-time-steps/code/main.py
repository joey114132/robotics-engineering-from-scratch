# 레슨 00/06: 컴퓨터는 아주 작은 시간 스텝을 되풀이해 움직인다. 새 위치 = 옛 위치 + 속도 x 스텝, 그리고 스텝 크기가 오차에 미치는 영향
G = 9.81


def move(position, speed, dt, steps):
    """Move at a steady speed: repeat 'new position = old position + speed * dt'."""
    for _ in range(steps):
        position = position + speed * dt
    return position


def positions(accel, seconds, dt):
    """Distance covered from rest at every step while speeding up by accel. The speed is updated first, then the position."""
    d, v, out = 0.0, 0.0, [0.0]
    for _ in range(round(seconds / dt)):
        v += accel * dt
        d += v * dt
        out.append(d)
    return out


def exact_distance(accel, seconds):
    """The true distance from rest, from the school formula half * accel * t squared."""
    return 0.5 * accel * seconds**2


if __name__ == "__main__":
    print("ball dropped for 1 s, true:", exact_distance(G, 1.0))
    for dt in (0.5, 0.1, 0.01):
        print(f"  step {dt}: {positions(G, 1.0, dt)[-1]:.3f}")
