# Gravity Compensation

> A position loop pays for every error in your gravity model, and the bill is the residual divided by kp.

**Type:** Build   **Prerequisites:** 01/02 Forward Kinematics   **Time:** ~15 minutes

## In Plain Words

A bench arm holding its hand out needs motor torque to carry its own weight. Gravity compensation is the motor's guess of that weight, added in advance, like a friend lifting a tray by guessing how heavy it is.

If the guess is too low, the leftover weight pulls the hand down. If too high, the hand rises. The position controller pushes back on that error, and its gain kp is the push per unit of sag, so a lower kp lets the same mistake move the hand farther.

## The Problem

You lower the position gain `kp` (how hard the motor pushes the arm back per radian of error) to soften an arm so a person can push it. The arm now sags below its commanded pose, or floats above it, and the softer you go the worse it gets. Gravity compensation was supposed to prevent exactly this.

## The Concept

![Residual over kp](../assets/diagram-sag-flow.png)

*Follow the red box: `ff` is the torque the model feeds forward in advance and `tau_g` is what gravity really needs. Their gap, the residual (the model's error), is left to the position spring.*

At rest the torques balance: `kp * (q_des - q) + ff = tau_g(q)`, where `q_des - q` is the commanded angle minus the real one, so `kp` times it acts like a spring. Rearranged, the sag `q - q_des` is `(ff - tau_g) / kp`, to first order (small errors). Angles are measured upward, so negative sag is droop.

![Three cases](../assets/diagram-sag-cases.png)

*Pick your case: a light model droops, an exact model holds, a heavy model floats up.*

Example: the lesson's two-link arm (masses 2 and 1 kg, links 0.4 m) held straight out, `kp = 30`. Gravity needs 9.81 Nm at the shoulder (`gravity_torque`). A model 20% too light misses `0.2 * 9.81 = 1.96` Nm, which the spring turns into `1.96 / 30 = 0.065` rad, about 3.7 degrees of droop. A model 20% too heavy misses 1.96 Nm the other way, so the arm floats up about 3.7 degrees (the exact solve gives 3.70 and 3.79).

![Two models](../assets/clip-example.mp4)

*Same `kp = 30`. Each amber ball is where an exact model holds the fingertip: the left arm droops below it, the right floats above. Sag drawn 6 times larger.*

![Sag against kp](../assets/fig-gravity-sag.png)

*Left: halving kp doubles the error either way. Right: a soft kp leaves the arm below the commanded line.*

## Build It

Gravity torque of a planar two-link arm, angles from the horizontal.

```python
t2 = m2*lc2*g*np.cos(q1+q2)
t1 = (m1*lc1 + m2*l1)*g*np.cos(q1) + t2
```

`steady_state()` solves the balance equation and raises if no equilibrium exists, which happens when `kp` is below the gravity gradient (how fast gravity torque grows with angle). `sag()` returns `q - q_des`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/02-gravity-compensation -q
python3 phases/03-dynamics-and-control/02-gravity-compensation/code/figure.py
```

## Use It

Real arms take `tau_g` from a rigid-body model such as the bias force at zero velocity in MuJoCo. CAD inertias are often wrong, so measure sag at two poses and fit a scale. Droop means the model is too light.

## Ship It

`outputs/skill-gravity-comp-check.md` turns a measured sag into a model-error estimate.

## Exercises

1. Add a third joint and check that the horizontal pose is still the worst case.
2. Fit one mass scale from sag at `kp = 100` and predict the sag at `kp = 50`.
3. Show that the first-order estimate degrades when `kp` is close to the gravity gradient.
