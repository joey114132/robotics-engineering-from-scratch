# Impedance Control

> Impedance control does not track a position. It decides how the joint pushes back.

**Type:** Build   **Prerequisites:** 03/01 The Sampling Limit, 03/02 Gravity Compensation   **Time:** ~15 minutes

## The Problem

A stiff position loop fights every touch with maximum force. A robot that hands over a cup needs the opposite: a chosen stiffness and a chosen damping, so a push produces a predictable, bounded deflection instead of a fight.

## The Concept

![Spring, damper and gravity feedforward act on one joint](../assets/diagram-impedance-structure.png)

*The controller adds a virtual spring, a virtual damper and gravity feedforward. The world pushes with `F`.*

The law is `tau = K (q_des - q) - D qd + tau_g`. With a constant push `F` the joint settles at `F / K`. The damping ratio `zeta = D / (2 sqrt(K J))` sets the shape of the approach: at `zeta = 1` there is no overshoot, and for `zeta < 1` the overshoot fraction is `exp(-pi zeta / sqrt(1 - zeta^2))`, about 0.53 for `zeta = 0.2`.

![Step response for three damping ratios, and deflection against K](../assets/fig-impedance-response.png)

*Left: the same `K` and three `zeta` values all settle at `F / K`, but only the damping changes the overshoot. Right: doubling `K` halves the deflection.*

![Choosing K and D in four steps](../assets/diagram-impedance-recipe.png)

*Pick `K` from the deflection budget, `D` from the damping ratio, then check the sampling limit of lesson 03/01.*

## Build It

```python
def impedance_torque(q, qd, q_des, K, D, tau_g):
    return K*(q_des - q) - D*qd + tau_g

def damping_for_zeta(K, J, zeta):
    return 2*zeta*np.sqrt(K*J)
```

`simulate()` pushes a 1-DOF joint with a constant external torque using semi-implicit Euler. Tests check the deflection against `F / K` to 1%, that doubling `K` halves it, that `zeta = 1` never overshoots, and that `zeta = 0.2` matches the formula within 3 percentage points.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/03-impedance-control -q
python3 phases/03-dynamics-and-control/03-impedance-control/code/figure.py
```

## Use It

Torque-controlled arms expose joint impedance as `K` and `D` per joint, sometimes with Cartesian impedance on top through the Jacobian transpose. To choose `K`, take the largest push you expect and the largest deflection you accept: `K = F_max / x_max`.

## Ship It

`outputs/skill-impedance-check.md` checks a `K`, `D` choice against a deflection budget and the sampling limit.

## Exercises

1. Add friction and find the new steady state under a small force.
2. Replace the constant force with a step that reverses. Compare the settling time for `zeta` of 0.7 and 1.
3. Use the sampling-limit check to find the largest `D` a 1 kHz loop allows for `J = 0.05`.
