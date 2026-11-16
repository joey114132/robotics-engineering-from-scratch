# Complementary Filter

> Learn how to combine a smooth-but-drifting sensor with a jittery-but-honest one to track tilt.

**Type:** Build   **Prerequisites:** 07/03 IMU Integration and Drift   **Time:** ~15 minutes

## In Plain Words

Adding up a gyro's readings follows quick tilts smoothly but drifts. The accelerometer gives the tilt from gravity but jitters. A complementary filter takes quick changes from the gyro and the slow average from the accelerometer.

## Key Terms

- **Gyro**: measures turning speed. Adding its readings up gives a smooth angle that drifts.
- **Accelerometer**: feels gravity, so it gives tilt directly, but jitters.
- **Time constant (`tau`)**: how long the gyro is trusted before the accelerometer takes over.
- **High-pass / low-pass**: a filter that keeps fast changes, or one that keeps the slow average.
- **Crossover**: the frequency (cycles per second, Hz) where both paths carry equal weight.
- **Bias**: a small steady sensor error.

## The Problem

A robot must balance upright. Tilt from its accelerometer alone jitters, so the controller shakes. The integrated gyro is smooth but creeps off until the robot thinks it leans while standing straight.

## The Concept

A balancing robot needs a tilt that is both smooth and honest over minutes.

![Two sensors](../assets/diagram-comp-split.png)

*Gyro through a high-pass, accelerometer through a low-pass, then add.*

Each step, `theta = a (theta + gyro dt) + (1 - a) acc`, where `acc` is the accelerometer's tilt and `a = tau / (tau + dt)`.

The accelerometer path is a low-pass and the gyro path a high-pass. Their weights add to 1. They cross at `1 / (2 pi tau)` Hz.

![Estimates and crossover](../assets/fig-tilt-estimates.png)

*Left: at `tau = 0.40 s` the fused tilt sits on the truth. Right: the crossover is 0.40 Hz.*

The gyro is trusted for about `tau` seconds, so a constant bias `b` piles up to an error of `tau b`. Accelerometer noise `s` leaves variance about `s^2 dt / (2 tau)`. Minimising `(tau b)^2 + s^2 dt / (2 tau)` gives `tau^3 = s^2 dt / (4 b^2)`.

![Tuning tau](../assets/diagram-comp-tau.png)

*Small `tau` lets noise through, large `tau` lets bias through.*

![Error against tau](../assets/fig-tau-tradeoff.png)

*Simulation matches; the minimum is at 0.40 s.*

Take `b = 0.01 rad/s`, `s = 0.05 rad`, `dt = 0.01 s`. Then `tau = 2 s` leaves a bias error of `2 * 0.01 = 0.02 rad`, `tau = 0.05 s` a noise error of 0.015 rad, and `tau = 0.40 s` only 0.004 and 0.0056, together `0.0068 rad`.

![Three filters](../assets/clip-example.mp4)

*Small `tau`: noise shakes the board. Large `tau`: a steady lean. The middle is closest to level. Errors drawn 10 times larger.*

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

`imu_complementary_filter` in `imu_tools` fuses gyro, accelerometer and optional magnetic readings.

Sources: imu_tools README, https://raw.githubusercontent.com/CCNYRoboticsLab/imu_tools/humble/README.md (2026-11-09).

## Ship It

`outputs/skill-complementary-filter-check.md` checks the time constant against the measured bias and noise.

## Exercises

1. Compute the bias error for `tau = 5 s`, `b = 0.01 rad/s`.
2. Halve `s` and predict the new best `tau`.
3. If the accelerometer is noisy only during shaking, what should `tau` do?
