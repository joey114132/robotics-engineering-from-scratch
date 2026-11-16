# Differential Drive and Odometry

> Learn why a robot can say it came home when it did not, and what causes it.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3)   **Time:** ~15 minutes

## In Plain Words

Walk a square but turn a little less than [90°](https://mathworld.wolfram.com/RightAngle.html) at each corner. A notebook that logs every turn as [90°](https://mathworld.wolfram.com/RightAngle.html) draws a closed square, yet you miss the start.

A robot with a wrong wheel size does the same. Its notebook shares the wrong value, so the path closes on paper.

## Key Terms

- **Differential drive**: a robot that steers by spinning its two wheels at different speeds.
- **Odometry**: a position guess made by adding up how far the wheels turned.
- **Wheel radius (`r`)**: the distance from a wheel's center to its edge.
- **Track width (`b`)**: the distance between the two wheels.
- **Dead reckoning**: tracking position by adding up each small movement from a known start.
- **rad/s**: radians per second, a spin speed. One full turn is about 6.28 radians.

## The Problem

Picture a robot drawing a 2 m square. Odometry says it is back at the start; a tape measure says 18 cm off. The wheels turned as commanded, so the config's wheel radius or track width is wrong.

## The Concept

A real robot with wrong wheel numbers trusts a wrong position, and every plan built on it is off.

![Wheel speeds to pose](../assets/diagram-wheels-to-pose.png)

*Speeds add up to the pose (position and heading).*

`wl` and `wr` are the wheel spin speeds in rad/s. A wheel's edge moves `r` times its spin, so forward speed is the average of the two edges, `v = r (wr + wl) / 2`. The turn rate `w` (heading change per second) is their difference over `b`, `w = r (wr - wl) / b`.

With `r = 0.05 m`, `b = 0.30 m` and wheels at 10 and 14 rad/s, `v = 0.6 m/s` and `w = 0.67 rad/s`. The robot circles left with radius `v / w = 0.9 m`.

![Two rovers](../assets/clip-example.mp4)

*Blue: 10 and 10. Green: 10 and 14.*

![One hidden gap](../assets/diagram-two-errors.png)

*Same wrong `r` and `b`, so the loop closes.*

![Odometry drift](../assets/fig-odometry-drift.png)

*Gray: odometry's belief. Orange: real.*

Say the real `b` is 2% larger. Each turn is `a = 88.2°`, not 90°, so the sides no longer cancel and the robot ends 0.18 m from the start. The gap is `L |1 + e^(ia) + e^(2ia) + e^(3ia)|` (tested), where `L` is a side and `e^(ia)` an arrow turned by `a`.

## Build It

```python
def wheels_to_twist(wl, wr, r, b):
    return r * (wr + wl) / 2, r * (wr - wl) / b

def dead_reckon(wl, wr, dt, r, b, pose0=(0.0, 0.0, 0.0)):
    v, w = wheels_to_twist(np.asarray(wl, float), np.asarray(wr, float), r, b)
    dth = w * dt
    step = v * dt * np.sinc(dth / (2 * np.pi))  # chord of the arc
    th = pose0[2] + np.cumsum(dth) - dth / 2
```

`square_wheels()` plans the square; `closure_error()` replays it with other `r` and `b`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/01-differential-drive-and-odometry -q
python3 phases/08-mobile-robots/01-differential-drive-and-odometry/code/main.py
```

## Use It

ROS 2's diff_drive_controller needs `wheel_separation` and `wheel_radius`. Its docs say a wrong separation misbehaves in curves.

Sources: control.ros.org, diff_drive_controller user doc (jazzy), opened 2026-11-09.

## Ship It

`outputs/skill-odometry-calibration-check.md` turns a closure gap into a suspected parameter and a calibration run.

## Exercises

1. Give the wheels different radii; show that a line bends.
2. Drive clockwise; show the gap mirrors the counter-clockwise one.
3. Add 1% wheel slip on turns; find which error it looks like.
