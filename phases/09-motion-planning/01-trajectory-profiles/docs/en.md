# Trajectory Profiles

> Joining two points with a path is easy. A path the motor can follow without a jerk takes six conditions, not four.

**Type:** Build   **Prerequisites:** high-school calculus   **Time:** ~15 minutes

## In Plain Words

An elevator can leave a floor without an instant jump in speed and still give you a jolt. The floor suddenly pushes harder upward on
your feet because the elevator's acceleration changes abruptly.

Trajectory profiles choose how a robot moves between positions. Reaching each end at rest does not stop acceleration from jumping
there. A quintic profile also brings acceleration to zero at the ends, so the motor's effort need not jump when the move begins or
ends.

## The Problem

A joint moves between two poses along a smooth-looking curve and still knocks at the start. The curve reaches the right place with zero speed at both ends, so position and velocity are fine. Acceleration is the culprit: it jumps from zero to a large value in one control tick.

## The Concept

![Three profiles and what each does to acceleration](../assets/diagram-profile-choice.png)

*Cubic, quintic and trapezoid profiles make the same move. They differ in how acceleration behaves at the ends.*

A polynomial in time has one coefficient per condition. Position and velocity at both ends give four conditions, so a cubic. Adding acceleration at both ends gives six, so a quintic. With `s = t/T` and `d = qf - q0`, the quintic is `q0 + d(10 s^3 - 15 s^4 + 6 s^5)`.

![Position, velocity and acceleration side by side](../assets/fig-profiles.png)

*All three reach the target at rest. Only the quintic starts and ends with acceleration zero.*

![How a step becomes a jerk](../assets/diagram-jerk-chain.png)

*A step in acceleration is a spike in jerk, and the motor sees it as a step in torque.*

![Peak jerk against sample period](../assets/fig-jerk-vs-dt.png)

*Halve the sample period and the cubic and trapezoid jerk doubles. The quintic stays at `60 d / T^3`.*

## Build It

```python
def quintic(q0, qf, T):
    d = qf - q0
    return np.array([q0, 0.0, 0.0, 10*d/T**3, -15*d/T**4, 6*d/T**5])
```

`poly` evaluates position, velocity and acceleration from coefficients. `trapezoid` accelerates for `ta`, cruises at `d/(T-ta)`, then decelerates. `peak_jerk` treats the joint as resting before and after the move, which is where the step comes from.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/01-trajectory-profiles -q
python3 phases/09-motion-planning/01-trajectory-profiles/code/main.py
```

## Use It

SciPy's `BPoly.from_derivatives` builds the same quintic from end derivatives, and the last test compares them.

Sources: Craig, *Introduction to Robotics*, 3rd ed., ch. 7 (trajectory generation).

## Ship It

`outputs/skill-trajectory-profile-check.md` checks a profile's boundary conditions and jerk before it reaches a joint.

## Exercises

1. Add a seventh condition, zero jerk at both ends, and say which degree you need.
2. For a trapezoid, find the smallest `ta` that keeps peak acceleration below a given limit.
3. Time-scale a quintic to `2T` and show that peak acceleration drops by a factor of four.
