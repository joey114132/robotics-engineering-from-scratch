# IMU Integration and Drift

> Integrating a sensor that has a tiny constant error turns that error into a line, a parabola or a cubic, and gravity is the channel that makes it cubic.

**Type:** Build   **Prerequisites:** 07/02 Kalman Filter   **Time:** ~15 minutes

## In Plain Words

A robot sits still, but its gyro, the turning-speed sensor, reads a tiny turn that is not there. Adding those readings up, the robot thinks it is slowly tilting.

Its accelerometer feels gravity even at rest, and the robot removes gravity using its tilt guess. With a wrong tilt, some gravity is left over as a sideways push that is not real. Adding up the push gives speed and adding up speed gives distance, so the robot believes it is rolling away.

## The Problem

A still robot's IMU (a gyro plus an accelerometer) reads almost no turning and no push beyond gravity. Give it a gyro bias (a small steady error) of 0.01 rad/s and an accelerometer bias of 0.05 m/s^2. Adding up for 20 seconds says it turned 11 degrees and moved 10 m, and gravity makes it worse.

## The Concept

![Each integral raises the drift order](../assets/diagram-drift-orders.png)

*Follow each row. A gyro is added up once for an angle, an accelerometer twice for a position, and each time adds a power of `t`.*

Integrating means adding readings up over time. A constant gyro bias `b` gives an angle error of `b t`. A constant accelerometer bias `a` gives a velocity error `a t` and a position error `a t^2 / 2`. White noise of size `sigma` per sample, `dt` apart, adds a random walk of typical size `sigma * sqrt(dt * t)`.

![Error against derived formulas](../assets/fig-imu-drift.png)

*Fifteen noisy runs wander around `b t` (angle) and `a t^2 / 2` (position).*

![Gyro bias leaks via gravity](../assets/diagram-gravity-leak.png)

*A tilt error makes the robot subtract gravity the wrong way. The leftover looks like real acceleration.*

![Cubic growth overtakes quadratic](../assets/fig-gravity-leak.png)

*Watch the cubic curve (gyro bias) pass the quadratic one (accelerometer bias) after about 1.5 s. The tilt error is `b t`, so the fake acceleration is `g sin(b t)`, about `g b t` for small angles. Adding up a ramp twice gives `g b t^3 / 6`.*

Take a gyro bias of `0.01 rad/s`. After 10 s the tilt is wrong by `0.1 rad`, so gravity leaves a fake `9.81 * sin(0.1) = 0.98 m/s^2`. The position error is about `9.81 * 0.01 * 10^3 / 6 = 16 m`, while an accelerometer bias of `0.05 m/s^2` gives only `0.05 * 10^2 / 2 = 2.5 m`.

![Still robot slides](../assets/clip-example.mp4)

*Watch the amber copy while the green robot stays put. Its tilt grows, the red arrow is the fake push, and the copy slides faster. Tilt is drawn 5 times larger, 10 s play in 5 s, 1 m as 0.1 m.*

## Build It

```python
meas = omega_true + bias + sigma * rng.standard_normal((n, runs))
angle = np.cumsum(meas, axis=0) * dt

fake_a = G * np.sin(bias_g * t)          # tilt error b*t leaks gravity
pos = np.cumsum(np.cumsum(fake_a) * dt) * dt
```

Tests compare the sums with the exact discrete formulas and the derived `b t`, `a t^2 / 2` and `g b t^3 / 6`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/03-imu-integration-and-drift -q
```

## Use It

`imu_filter_madgwick` in `imu_tools` fuses gyro, accelerometer and optionally magnetic readings into an orientation, so it must correct this drift. Feed it a stationary recording and check the angle stops drifting.

Sources: imu_tools README, https://github.com/CCNYRoboticsLab/imu_tools (opened 2026-11-09).

## Ship It

`outputs/skill-imu-drift-check.md` estimates how long an IMU-only estimate stays usable.

## Exercises

1. Find when the angle error reaches 1 degree at `b = 0.01 rad/s`.
2. Double `dt`: does the 10 s angle error change?
3. Write the position error if the tilt error stays at its 5 s value.
