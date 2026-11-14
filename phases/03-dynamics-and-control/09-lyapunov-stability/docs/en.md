# Lyapunov Stability by Checking

> A stable system has an energy-like number that never rises, and you can test that on a computer.

**Type:** Build   **Prerequisites:** 03/04 PID and Tuning, 03/06 LQR   **Time:** ~15 minutes

## In Plain Words

Picture an arm hanging from its joint, pushed a little to one side. It swings back and forth, and each swing is smaller as the brake takes energy out. Add up its motion, height and spring energy, and you get a number that should only go down.

A Lyapunov function is such an energy-like number. If the brake sees the arm's speed late, it pushes along with the swing and adds energy instead.

## The Problem

The only stability test you know is "I simulated it and it settled." A run from rest sits still even when the system is unstable, and a run from one start misses the corner of state space where it blows up. You need a test that covers every state.

## The Concept

![The Lyapunov test](../assets/diagram-lyapunov-logic.png)

*Choose V, then check the sign of its slope. You never solve the motion.*

For a pendulum under PD control (a spring on the angle `q`, a brake on the rate `w`), take `V = 1/2 w^2 + (g/l)(1 - cos q) + 1/2 kp q^2`: kinetic, gravity and spring energy. Differentiating along the motion gives `dV/dt = -(c + kd) w^2`, where `c` is the joint's own friction. Spring and gravity only trade energy with the motion, so they cancel. So `dV/dt <= 0` everywhere exactly when `c + kd >= 0`.

Example: `kd = -1`, a brake that pushes with the motion, and `c = 0.1` give `dV/dt = 0.9 w^2`: at `w = 2` rad/s V grows by 3.6 per second. Rest is an equilibrium, so a run from rest never moves.

![Rest, nudged and damped](../assets/clip-example.mp4)

*The blue arms share `kd = -1`. The left one never moves from rest. The middle one, nudged 0.1 rad, swings wider each time. The green arm (`kd = 2`) is nudged too and settles. 1.5x speed.*

![One run versus a sweep](../assets/diagram-lyapunov-sweep.png)

*A run from rest looks stable. A sweep of states finds a positive slope at once.*

![Arrows and level sets](../assets/fig-lyapunov-level-sets.png)

*Each arrow is where the state moves next, angle `q` across and rate `w` up. Grey curves are level sets of V. Blue arrows do not point outward. Orange arrows do, and V grows there. With `kd = -1` almost every arrow is orange.*

![A late rate signal](../assets/fig-lyapunov-delay.png)

*Same gains, `kd = 5`, but the controller sees the rate late. At 300 ms V climbs instead of falling.*

## Build It

```python
grad = np.array([(V(x + h*e, p) - V(x - h*e, p)) / (2*h) for e in np.eye(2)])
vdot = grad @ f(x, p)          # dV/dt along the motion
```

`check()` samples states and returns the largest `vdot` and its location. Tests check that `V` is positive, that `vdot` equals `-(c + kd) w^2`, that stable gains pass and negative damping is caught, and that a delayed rate raises V. A sampled check finds counterexamples but proves nothing.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/09-lyapunov-stability -q
python3 phases/03-dynamics-and-control/09-lyapunov-stability/code/figure.py
```

## Use It

To search for a counterexample, minimize `-vdot` over the operating bounds with a solver such as SciPy's `minimize`. Report the corresponding maximum `vdot` and compare it with the sampled one. For a proof, an SOS or SMT tool must confirm the sign.

## Ship It

`outputs/skill-lyapunov-check.md` turns a stability claim into a candidate V and a sweep.

## Exercises

1. Set `kp = 0` and explain what happens to the sign of V away from the origin.
2. Find the delay at which `kd = 5` first fails to settle.
3. Add a friction term `c |w| w` and recompute `vdot` by hand.
