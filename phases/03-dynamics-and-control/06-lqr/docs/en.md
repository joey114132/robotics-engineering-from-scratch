# LQR: Gains from Cost, Not from Guessing

> Say how much you hate error against effort, and the Riccati recursion hands back the gain.

**Type:** Build   **Prerequisites:** 03/04 PID and Tuning   **Time:** ~15 minutes

## In Plain Words

Imagine pushing a toy car to a stop line. A hard push gets it there quickly but costs effort. A gentle push saves effort but takes longer.

LQR uses a model of the car to weigh error against effort. Q says how much error hurts and R says how much effort hurts. A larger R makes big pushes costly, which softens the response. It is not a hard limit.

## The Problem

You have a state-space model (the state is what predicts the motion, like position and speed) and tune `kp` and `kd` by feel. The result is slow or violent, and you cannot say why. For one input, two states need two gains to guess. Six states need six.

## The Concept

![Weights to a gain](../assets/diagram-lqr-flow.png)

*You supply the model and two cost weights. The Riccati loop (repeat below) returns every entry of K.*

The cost is the sum over time of `x'Qx + u'Ru`, where `x` is the state, `u` the push, and the car model is `x+ = A x + B u`. `Q` prices error and `R` prices effort. Start with `P = Q` and repeat `K = (R + B'PB)^-1 B'PA`, then `P = Q + A'P(A - BK)`. When `P` (the cost still to come from each state) stops changing, `u = -Kx` is the cheapest feedback for that cost. The cost from state `x0` is then `x0'P x0`.

![R sets the trade](../assets/diagram-lqr-tradeoff.png)

*Raising R breaks nothing. Big pushes cost more.*

![Four values of R](../assets/fig-lqr-r-sweep.png)

*A double integrator (a car steered by acceleration) starting 1 m away. R = 0.01 settles fastest with an 8.7 m/s^2 first push. R = 10 pushes 0.3, slowly.*

Example: stopping early gives a weak gain. With `R = 1`, `Q = diag(1, 0.1)` and `dt = 0.05`, a car 1 m from the line gets `K = [0.005, 0.010]` (position gain, speed gain) after 1 loop and moves 0.09 m in 6 s. After 10 loops `K = [0.15, 0.11]` and it swings across the line at about 4.5 s. With a steady `P`, `K = [0.96, 1.42]` and the car is within 0.05 m of the line at 3 s.

![More loops](../assets/clip-example.mp4)

*Same car, `R = 1`, `K` from 1 loop, 10 loops and a steady `P`. The first car barely creeps, the second swings across the line, the green one settles.*

## Build It

```python
K = np.linalg.solve(R + B.T @ P @ B, B.T @ P @ A)
P = Q + A.T @ P @ (A - B @ K)      # repeat until P is steady
```

`dare()` loops these two lines, and `dare(max_iter=n)` stops after `n` loops. `rollout()` runs `u = -Kx` and adds up the cost. Tests check that the closed-loop eigenvalues are inside the unit circle, that `K` and `P` satisfy their equations, and that a larger `R` lowers the peak input.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/06-lqr -q
python3 phases/03-dynamics-and-control/06-lqr/code/figure.py
```

## Use It

SciPy's `scipy.linalg.solve_discrete_are` solves the same equation directly, so use it to cross-check `P`. Raising `R` can reduce effort for the tested starts; check the full rollout. Hard actuator limits need explicit constraints or separately validated saturation handling.

## Ship It

`outputs/skill-lqr-gain-review.md` reviews a Q and R choice by its closed-loop poles and peak input.

## Exercises

1. Make `Q` penalise velocity ten times more and describe how the response changes.
2. Estimate a constant input disturbance and cancel it with feedforward; keep LQR on the controllable position and velocity errors.
3. Find the `R` that keeps the peak input under 2 m/s^2 for a 1 m step.
