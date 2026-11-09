# Complementary Filter

> The gyro is right about fast changes and wrong about the long run, the accelerometer is the opposite, and one time constant decides who is believed when.

**Type:** Build   **Prerequisites:** 07/03 IMU Integration and Drift   **Time:** ~15 minutes

## The Problem

You estimate tilt from the accelerometer and the angle jitters so much that a balancing controller shakes. You switch to the integrated gyro and the angle is smooth, but it creeps away from the truth until the robot believes it is leaning when it stands straight.

## The Concept

![Two sensors, two weaknesses](../assets/diagram-comp-split.png)

*Pass the gyro through a high-pass, the accelerometer tilt through a low-pass, and add them.*

The filter is `theta = a (theta + gyro dt) + (1 - a) acc` with `a = tau / (tau + dt)`. In continuous time the accelerometer path is `1 / (1 + j w tau)` and the gyro path is `j w tau / (1 + j w tau)`. They add to exactly 1, so a true tilt passes through unchanged. They cross at `1 / (2 pi tau)` Hz, where each has gain `1 / sqrt(2)`.

![Three estimates and the crossover](../assets/fig-tilt-estimates.png)

*Left: with `tau = 0.40 s` the fused tilt sits on the truth, while the accelerometer is noisy and the gyro drifts. Right: below 0.40 Hz the accelerometer is trusted, above it the gyro.*

A constant gyro bias `b` leaves a steady error of exactly `tau b`. White accelerometer noise of std `s` leaves a variance of `s^2 (1 - a) / (1 + a)`. Minimising `(tau b)^2 + s^2 dt / (2 tau)` gives `tau^3 = s^2 dt / (4 b^2)`.

![Tuning tau](../assets/diagram-comp-tau.png)

*A small `tau` lets accelerometer noise through. A large `tau` lets gyro bias through.*

![Error against tau](../assets/fig-tau-tradeoff.png)

*Example values `b = 0.01 rad/s`, `s = 0.05 rad`, `dt = 0.01 s`. The simulation sits on the derived curve, and its minimum is at 0.40 s.*

## Build It

```python
def alpha(tau, dt):
    return tau / (tau + dt)

def complementary(gyro, acc, dt, tau, theta0=0.0):
    a, theta, out = alpha(tau, dt), np.full(gyro.shape[1], theta0, float), []
    for g, z in zip(gyro, acc):
        theta = a * (theta + g * dt) + (1 - a) * z
        out.append(theta)
    return np.array(out)
```

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/04-complementary-filter -q
```

## Use It

`imu_complementary_filter` in `imu_tools` fuses angular velocity, acceleration and optionally magnetic readings into an orientation quaternion by complementary fusion. Run it on a recording and compare its tilt with this lesson's `tau` trade-off.

Sources: imu_tools README, https://raw.githubusercontent.com/CCNYRoboticsLab/imu_tools/humble/README.md (opened 2026-11-09).

## Ship It

`outputs/skill-complementary-filter-check.md` checks the time constant against the measured bias and noise.

## Exercises

1. Compute the gyro-bias error for `tau = 2 s` and `b = 0.01 rad/s`, then check it in the code.
2. Halve `s` and predict the new best `tau`.
3. Replace the accelerometer with one that is noisy only when the robot shakes, and say what `tau` should do.
