# Differential Drive and Odometry

> Wheel speeds give you a pose only if you know two lengths exactly, and the estimate cannot tell you when you do not.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3)   **Time:** ~15 minutes

## The Problem

You drive a mobile robot around a 2 m square and the wheel odometry says it came back to the start. The tape measure says it stopped 18 cm away. The wheels turned exactly as commanded, so the motors are not at fault. The error is in two numbers you typed into a config file.

## The Concept

![From wheel speeds to a pose](../assets/diagram-wheels-to-pose.png)

*Two wheel speeds become a forward speed and a turn rate. Adding them up over time gives the pose.*

The forward speed is the average of the two wheel rims, `v = r (wr + wl) / 2`. The turn rate is their difference divided by the track width, `w = r (wr - wl) / b`. Dead reckoning adds `v dt` and `w dt` at every step.

![Two small errors, two different damages](../assets/diagram-two-errors.png)

*The estimate uses the same wrong `r` and `b` as the planner, so it still closes the loop and shows no sign of the problem.*

![The real path and the odometry path of one square](../assets/fig-odometry-drift.png)

*Left: a track width 2% too large leaves the real robot 0.18 m from the start. Right: the gap grows linearly, and a radius error of the same size does almost the same damage.*

Each corner turns by a wrong angle, and the four sides add up to a vector that no longer cancels. For a turn error `k`, the gap is `L |1 + e^(ia) + e^(2ia) + e^(3ia)|` with `a = (pi/2) / k`, and a test checks it.

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

`square_wheels()` plans the square with nominal `r` and `b`. `closure_error()` replays the commands with other `r` and `b`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/01-differential-drive-and-odometry -q
python3 phases/08-mobile-robots/01-differential-drive-and-odometry/code/main.py
```

## Use It

ROS 2's diff_drive_controller needs `wheel_separation` and `wheel_radius`. Its docs warn that a wrong separation makes the robot misbehave in curves and a wrong radius makes it move faster or slower than expected. It also offers `wheel_separation_multiplier` as a correction factor. Calibrate with a measured square.

Sources: control.ros.org, diff_drive_controller user doc (jazzy), opened 2026-11-09.

## Ship It

`outputs/skill-odometry-calibration-check.md` turns a measured closure gap into a suspected parameter and a calibration run.

## Exercises

1. Give the two wheels different radii and show that a straight line bends.
2. Drive the square clockwise and show that the gap vector is the mirror image of the counter-clockwise one.
3. Add 1% wheel slip on turns and find which error it looks like.
