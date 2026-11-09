# Computed Torque

> If you know the arm's equations, use them to cancel the arm, then control what is left.

**Type:** Build   **Prerequisites:** 03/03 Impedance Control, 03/04 PID and Tuning   **Time:** ~15 minutes

## The Problem

A joint-by-joint PD controller tracks a slow motion well. Make the same motion four times faster and the arm lags and wobbles, because the inertia and coupling torques that were small at low speed now dominate. Raising the gains runs into the limit of lesson 03/04.

## The Concept

![Why a joint-by-joint PD fails at speed](../assets/diagram-pd-blind-spot.png)

*The elbow angle changes the inertia, and fast swinging adds Coriolis torque. PD sees both as surprise pushes.*

For a horizontal 2-link arm the dynamics are `tau = M(q) qdd + h(q, qd)`. `M` is the inertia matrix and `h` holds the Coriolis and centripetal torques. Gravity is lesson 03/02's job and is left out here. Computed torque picks `tau = M(q) a + h(q, qd)` with `a = qdd_d + kd ed + kp e`. The model cancels the arm, so the error obeys `e'' + kd e' + kp e = 0`.

![Computed torque in two layers](../assets/diagram-computed-torque.png)

*The inner layer is the model. The outer layer is a plain PD on the error.*

![Inertia against elbow angle, and the torques PD ignores](../assets/fig-model-terms.png)

*Left: joint-1 inertia changes by a factor of about four with the elbow. Right: along the reference, the inertial and Coriolis torques are large.*

![Tracking error of PD and computed torque](../assets/fig-tracking-error.png)

*A 1 s swing with `omega = 20`. Computed torque with the exact model has about 300 times less error than PD, and with masses off by 20% it still has about 5 times less.*

## Build It

```python
M = mass(q, model)                      # 2x2, depends on the elbow angle
a = qdd_d + 2*w*(qd_d - qd) + w*w*(q_d - q)
tau = M @ a + coriolis(q, qd, model)    # Coriolis and centripetal terms
```

`main.py` holds the full `M` and `h` terms. Tests check `M` against the kinetic energy computed from Cartesian velocities, `M qdd + h` against a numeric Lagrangian, and that free motion conserves kinetic energy, which tests the Coriolis sign. Then PD and computed torque run on the same trajectory.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/05-computed-torque -q
python3 phases/03-dynamics-and-control/05-computed-torque/code/figure.py
```

## Use It

MuJoCo's `mj_inverse` returns `qfrc_inverse`, the torque for a given `qacc`. One test builds the same arm in MuJoCo and compares it with `inverse_dynamics` to 1e-9. Craig, Ch. 10, covers the nonlinear control law.

Sources: [MuJoCo API reference](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html), checked 2026-11-09.

## Ship It

`outputs/skill-computed-torque-check.md` reviews a model-based controller for model error and sampling.

## Exercises

1. Add gravity from lesson 03/02 to `h` and keep the energy test valid by adding the potential.
2. Scale one mass by 0.5 to 1.5 and plot the maximum error.
3. Run computed torque at 100 Hz instead of 1 kHz and see where the error floor moves.
