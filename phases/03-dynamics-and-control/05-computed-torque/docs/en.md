# Computed Torque

> Learn how to cancel an arm's own swing forces in advance, so a fast motion stays on track.

**Type:** Build   **Prerequisites:** 03/03 Impedance Control, 03/04 PID and Tuning   **Time:** ~15 minutes

## In Plain Words

A two-link arm sweeps across a table. With the elbow straight the same swing takes more shoulder torque, and a fast swing makes each link tug on the other.

Computed torque uses the arm's equations to work out the torque these effects demand, and supplies it in advance. A small correction handles the leftover error.

## Key Terms

- **Torque**: a twisting push, such as a motor's push on a joint.
- **Dynamics**: the equations linking torques to joint motion.
- **Computed torque**: using the arm's equations to cancel its dynamics, then controlling what is left.
- **Inertia matrix (`M`)**: how heavy the arm feels to each joint; it changes with the elbow angle.
- **Coriolis torque**: the pull links exert on each other when they swing fast.
- **PD controller**: pushes in proportion to how far the arm is from its plan, and brakes in proportion to its speed.

## The Problem

A simple controller (the program steering the arm) makes a robot arm follow a slow motion well. Make the same motion four times faster, and the arm lags and wobbles.

## The Concept

Fast motion makes an arm's links pull on each other, and a good controller predicts that. The arm's inertia and swing forces can be worked out from its equations, so the controller supplies them in advance and only fixes what is left.

![PD fails at speed](../assets/diagram-pd-blind-spot.png)

*A simple controller sees these forces as surprises.*

![Computed torque in two layers](../assets/diagram-computed-torque.png)

*Inner layer: cancel what the arm model predicts. Outer layer: fix the small leftover error.*

![Inertia and torques](../assets/fig-model-terms.png)

*The arm feels heavier with the elbow straight.*

![Tracking error](../assets/fig-tracking-error.png)

*A one-second swing: computed torque misses the planned path far less.*

[![Wrong masses](../assets/clip-example.jpg)](../assets/clip-example.mp4)

*Even with wrong model masses, the miss is smaller than with a simple controller.*

<details><summary>The math (optional)</summary>

For a horizontal 2-link arm `tau = M(q) qdd + h(q, qd)`. Computed torque uses `tau = M(q) a + h(q, qd)` with `a = qdd_d + kd ed + kp e`, so `e'' + kd e' + kp e = 0`. Both controllers are tuned to `omega = 20`; with the exact model computed torque has about 300 times less error. With real `m1` 20% larger and `m2` 20% smaller than modelled, PD peaks at 0.19 rad of error, computed torque at 0.038 rad. Joint-1 inertia changes about fourfold with the elbow. A test compares `mj_inverse` with `inverse_dynamics` to 1e-9.

</details>

## Build It

Three lines: get the arm's inertia matrix `M` for the current elbow angle, decide how fast the arm should speed up to follow the plan (the wanted acceleration), and add the swing terms.

```python
M = mass(q, model)                      # 2x2, depends on the elbow angle
a = qdd_d + 2*w*(qd_d - qd) + w*w*(q_d - q)
tau = M @ a + coriolis(q, qd, model)    # Coriolis and centripetal terms
```

Tests check `M` against the arm's energy of motion, the equations against a nudge-and-watch estimate, and that a free-swinging arm keeps its energy.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/05-computed-torque -q
python3 phases/03-dynamics-and-control/05-computed-torque/code/figure.py
```

## Use It

MuJoCo's `mj_inverse` returns the torque for a given acceleration. Craig, Ch. 10, covers the control law.

Sources: [MuJoCo API reference](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html), checked 2026-11-09.

## Ship It

`outputs/skill-computed-torque-check.md` reviews a model-based controller.

## Exercises

1. Make the model's masses 20% wrong and compare the error.
2. Run the controller 100 times a second instead of 1000.
3. Set one model mass to half, then 1.5 times its true value; compare.
