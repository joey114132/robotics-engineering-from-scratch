# Gravity Compensation

> Learn why a soft robot arm sags, and how the error in your weight guess decides how far.

**Type:** Build   **Prerequisites:** 01/02 Forward Kinematics   **Time:** ~15 minutes

## In Plain Words

A bench arm holding its hand out needs motor torque to carry its own weight. Gravity compensation is the motor's advance guess of that weight.

If the guess is too low the hand sags; too high, it rises. The position controller pushes back with gain kp per unit of error, so a lower kp lets the same mistake move the hand farther.

## Key Terms

- **Gravity compensation**: adding a model's estimate of the arm's weight as torque in advance.
- **Position gain (`kp`)**: how hard the motor pushes the arm back per radian of error.
- **Feedforward (`ff`)**: torque added in advance from a model, before any error appears.
- **Residual**: the model's error, the gap between `ff` and the torque gravity really needs.
- **Sag**: how far the arm ends up below (or above) its commanded angle.
- **Torque**: the twisting force a motor applies to a joint.

## The Problem

You soften a robot arm so a person can push it, by lowering the position gain `kp`. The arm now sags below its commanded pose, or floats above it.

## The Concept

A robot arm must hold up its own weight, and a wrong guess shows up as sag.

![Residual over kp](../assets/diagram-sag-flow.png)

*The gap between `ff` (model) and `tau_g` (gravity) is the residual.*

At rest the torques balance: `kp * (q_des - q) + ff = tau_g(q)`, so `kp` times the angle error acts like a spring. Rearranged, the sag `q - q_des` is `(ff - tau_g) / kp` to first order (small errors).

![Three cases](../assets/diagram-sag-cases.png)

*A light model droops, an exact model holds, a heavy model floats up.*

The lesson's two-link arm (2 kg, 1 kg, links 0.4 m) held straight out with `kp = 30` needs 9.81 Nm at the shoulder. A model 20% too light misses `0.2 * 9.81 = 1.96` Nm, so the spring droops `1.96 / 30 = 0.065` rad, about 3.7 degrees. A model 20% too heavy floats it up about 3.7 degrees (exact solve: 3.70 and 3.79).

![Two models](../assets/clip-example.mp4)

*Amber balls: where an exact model holds the fingertip. Sag drawn 6 times larger.*

![Sag against kp](../assets/fig-gravity-sag.png)

*Left: halving kp doubles the error. Right: a soft kp leaves the arm below the line.*

## Build It

```python
t2 = m2*lc2*g*np.cos(q1+q2)
t1 = (m1*lc1 + m2*l1)*g*np.cos(q1) + t2
```

`steady_state()` solves the balance and raises if no equilibrium exists (`kp` below the gravity gradient, how fast gravity torque grows). `sag()` returns `q - q_des`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/02-gravity-compensation -q
python3 phases/03-dynamics-and-control/02-gravity-compensation/code/figure.py
```

## Use It

Real arms take `tau_g` from a rigid-body model such as MuJoCo's bias force at zero velocity. CAD inertias are often wrong, so measure sag at two poses and fit a scale.

## Ship It

`outputs/skill-gravity-comp-check.md` turns a measured sag into a model-error estimate.

## Exercises

1. Add a third joint; is the horizontal pose still the worst case?
2. Fit one mass scale from sag at `kp = 100` and predict the sag at `kp = 50`.
3. Show the first-order estimate degrades near the gravity gradient.
