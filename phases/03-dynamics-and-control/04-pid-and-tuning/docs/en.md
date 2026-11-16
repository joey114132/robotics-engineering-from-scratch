# PID and Tuning

> Learn how the three parts of the most common controller work, and what goes wrong when you turn them up.

**Type:** Build   **Prerequisites:** 03/01 The Sampling Limit, 03/03 Impedance Control   **Time:** ~15 minutes

## In Plain Words

Steer a toy car to a stop line. P presses harder the farther it is from the line, D brakes harder the faster it moves, and I adds push the longer it stays short, beating a steady headwind.

With the throttle fully down, I keeps counting though it cannot add push, and the stored push shoves the car past the line. Anti-windup stops that.

## Key Terms

- **PID**: a controller that adds a P term (the error), an I term (the error summed over time) and a D term (a speed brake).
- **Steady offset**: the error left when a constant load pushes against P+D alone.
- **Saturation**: the motor is at its torque limit and cannot push harder.
- **Windup**: the integral keeps growing while saturated, then causes overshoot.
- **Eigenvalue**: a number for how much one motion pattern is multiplied per tick; the loop is stable if all are below 1 in size.
- **Plant**: the thing being controlled, here the joint and motor.

## The Problem

A robot joint oscillated, so someone raised `kp` (push per unit of error) and `kd` (brake per unit of speed). Now it buzzes: the joint, the motor's torque limit and the control period each cap the gains.

## The Concept

Most robot joints use PID control, so know what each part does and where it fails.

![Three terms, one limit](../assets/diagram-pid-structure.png)

*Three terms add up and the motor clips the sum at `umax`.*

![P, P+D and P+I+D](../assets/fig-pid-terms.png)

*A load steps in at 5 s. P+D settles `load / kp` below the target; only I brings it back.*

![Two toy cars hold a line while a steady push arrives](../assets/clip-example.mp4)

*A steady push of 20 arrives. With `kp = 100`, blue (P+D) stays `20 / 100 = 0.2` short; green (P+I+D) is pushed back, then returns.*

Windup: I keeps adding up error at saturation and shrinks only after the error changes sign, so the car overshoots.

![Windup](../assets/diagram-windup.png)

*Conditional integration (the clamp) stops adding while saturated and the error would push deeper.*

![Clamped windup](../assets/fig-windup.png)

*Orange: no clamp; it overshoots by about 1.5 rad.*

A second limit: the loop is stable only while its eigenvalues stay below 1 in size, and `kd` above about `2J/dt` breaks that.

![Raised gains](../assets/fig-raised-gains.png)

*Left: the torque command after raising gains. Right: the largest eigenvalue passes 1 near `kd = 2J/dt`.*

## Build It

```python
raw = kp * e + I - kd * v
u = np.clip(raw, -umax, umax)
if u == raw or e * raw < 0:      # conditional integration
    I += ki * e * dt
v += dt / J * (u - b * v - load)
```

`simulate()` runs this loop; `spectral_radius()` gives the stability test. Tests check the offset `load / kp` and windup against the clamp.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/04-pid-and-tuning -q
python3 phases/03-dynamics-and-control/04-pid-and-tuning/code/figure.py
```

## Use It

ROS 2 `control_toolbox` offers `none`, `back_calculation` and `conditional_integration` anti-windup, chosen per joint via `gains.<dof_names>.antiwindup_strategy`. Compare with this lesson's clamp (Craig 9.7).

Sources: [control_toolbox docs](https://control.ros.org/master/doc/control_toolbox/doc/index.html), [PID controller user doc](https://control.ros.org/rolling/doc/ros2_controllers/pid_controller/doc/userdoc.html), checked 2026-11-09.

## Ship It

`outputs/skill-pid-tuning-check.md` reviews a gain change for offset, windup and the sampling limit.

## Exercises

1. Try back-calculation instead and compare the overshoot.
2. Put the derivative on the error.
3. Find the largest `kp` keeping the spectral radius below 1 at `kd = 20`.
