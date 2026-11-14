# PID and Tuning

> P pushes now, I remembers the past, D brakes. Each fixes one problem and causes another.

**Type:** Build   **Prerequisites:** 03/01 The Sampling Limit, 03/03 Impedance Control   **Time:** ~15 minutes

## In Plain Words

Imagine steering a toy car to a stop line with a throttle. P presses harder the farther the car is from the line. D brakes harder the faster it moves. I adds push the longer the car stays short, which beats a steady headwind.

With the throttle pressed all the way down, I cannot add real push but keeps counting. That stored push shoves the car on past the line. Anti-windup stops the counting while the throttle is at its limit.

## The Problem

A joint oscillated, so someone raised `kp` (push per unit of error) and `kd` (brake per unit of speed) to stiffen it. Now it buzzes and the motor runs hot. Each PID gain looks like an independent knob, but the joint, the motor's torque limit and the control period each cap it.

## The Concept

![Three terms, one limit](../assets/diagram-pid-structure.png)

*Three terms add up and the motor clips the sum at `umax`. The joint has inertia `J`, friction `b` and a load; the controller sees only angle and velocity.*

![P, P+D and P+I+D](../assets/fig-pid-terms.png)

*Watch each curve after 5 s, when a steady load steps in. With P+D the joint settles `load / kp` below the target. Only the integral term brings it back.*

![Two toy cars hold a line while a steady push arrives](../assets/clip-example.mp4)

*Same case, toy cars. A steady push of 20 arrives (red arrows). With `kp = 100`, the blue car (P+D) stays `20 / 100 = 0.2` short of the line. The green car (P+I+D) is pushed back, then returns.*

The integral term (I) adds up error and keeps adding even when the motor is at its limit (saturated). It shrinks only after the error changes sign, so the car must overshoot to pay it back. That is windup.

![Windup](../assets/diagram-windup.png)

*Follow the red boxes. The fix used here, conditional integration (the clamp), stops adding while the motor is saturated and the error would push it deeper.*

![Clamped windup](../assets/fig-windup.png)

*The orange curve is the joint without the clamp: same gains and limit, and it overshoots the target by about 1.5 rad.*

Raising gains has a second limit, lesson 03/01 again. The loop is stable only while the eigenvalues of its 2x2 update matrix (how much each motion pattern is multiplied per tick) stay below 1 in size. `kd` above about `2J/dt` breaks that and flips the command every tick.

![Raised gains](../assets/fig-raised-gains.png)

*Left: the torque command after the gain change. Right: the largest eigenvalue magnitude leaves 1 near `kd = 2J/dt`.*

## Build It

```python
raw = kp * e + I - kd * v
u = np.clip(raw, -umax, umax)
if u == raw or e * raw < 0:      # conditional integration
    I += ki * e * dt
v += dt / J * (u - b * v - load)
```

`simulate()` runs this loop. `closed_loop_matrix()` and `spectral_radius()` (largest eigenvalue size) give the stability test. Tests check the offset `load / kp`, the effect of I and D, and windup against the clamp.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/04-pid-and-tuning -q
python3 phases/03-dynamics-and-control/04-pid-and-tuning/code/figure.py
```

## Use It

ROS 2 `control_toolbox` offers `none`, `back_calculation` and `conditional_integration` anti-windup strategies; `pid_controller` picks one per joint via `gains.<dof_names>.antiwindup_strategy`. Compare its conditional integration on your plant with this lesson's clamp. Craig 9.7 covers the offset argument.

Sources: [control_toolbox docs](https://control.ros.org/master/doc/control_toolbox/doc/index.html) (the three strategies), [PID controller user doc](https://control.ros.org/rolling/doc/ros2_controllers/pid_controller/doc/userdoc.html) (the per-joint setting), checked 2026-11-09.

## Ship It

`outputs/skill-pid-tuning-check.md` reviews a gain change for offset, windup and the sampling limit.

## Exercises

1. Replace conditional integration with back-calculation and compare the overshoot.
2. Put the derivative on the error instead of the velocity and watch the setpoint step.
3. Find the largest `kp` that keeps the spectral radius below 1 at `kd = 20`.
