# 레슨 00/01: 장난감 자동차가 sense, think, act 를 되풀이해서 벽 앞에서 멈춘다
WALL, STOP_AT, SPEED, DT = 3.0, 0.5, 1.0, 0.1   # metres, metres, metres per second, seconds per loop


def sense(position, wall=WALL):
    return wall - position              # a distance sensor: how far is the wall?


def think(distance, stop_at=STOP_AT):
    return SPEED if distance > stop_at else 0.0   # far away: drive; close: stop


def act(position, speed, dt=DT):
    return position + speed * dt        # the wheels turn for one short moment


def drive(wall=WALL, seconds=6.0, dt=DT):
    """The robot loop: sense, think, act, over and over. Returns what happened on every pass."""
    position, run = 0.0, {"position": [], "distance": [], "speed": []}
    for _ in range(round(seconds / dt) + 1):
        distance = sense(position, wall)
        speed = think(distance)
        for key, value in (("position", position), ("distance", distance), ("speed", speed)):
            run[key].append(value)
        position = act(position, speed, dt)
    return run


def blind_drive(speed=SPEED, seconds=4.0, dt=DT):
    """No sensing, no thinking: just 'drive for a fixed time'. Returns where the car ends up."""
    position = 0.0
    for _ in range(round(seconds / dt)):
        position = act(position, speed, dt)
    return position


if __name__ == "__main__":
    run = drive()
    print(f"loop car stops {run['distance'][-1]:.1f} m from the wall")
    print(f"blind car ends {blind_drive():.1f} m from the start, the wall is at {WALL} m")
