# Force and Hybrid Control

> Position control turns every error in your stiffness guess into a force error. A force loop measures the force, so the guess drops out.

**Type:** Build   **Prerequisites:** 11/01 Contact Models   **Time:** ~15 minutes

## In Plain Words

Wiping a desk means moving a sponge across it while pressing down. Pushing to a fixed depth gives a different force
on a softer sponge.

Force control measures the push, moving deeper when it is weak and backing off when it is strong. Hybrid control gives the
sliding direction a position target and the pressing direction a force target. That lets the tool follow bumps while
keeping its push.

## The Problem

A tool must press a sponge with 10 N. Stiffness is the newtons pushed back per metre squeezed. You assume 5000 N/m and command a 2 mm squeeze (10 / 5000). But the sponge top sits 0.4 mm lower than you assumed, so only 1.6 mm gets squeezed. Stiffness sets the force: 1000 N/m gives 1.6 N, the assumed 5000 N/m gives 8 N, 25000 N/m gives 40 N.

![Three arms](../assets/clip-example.mp4)

*Red bars (1.6 cm per newton) show each sponge's push back.*

## The Concept

![Why position control misses the force](../assets/diagram-position-miss.png)

*The command is right only for the assumed stiffness and height; the real ones set the force you get.*

![Force against time and against stiffness for both controllers](../assets/fig-force-vs-stiffness.png)

*Left: the force loop reaches 10 N on every surface, slower on soft ones. Right: position control's force grows with stiffness.*

The force loop moves the tool tip at speed `v = ki * (fd - f)`: `fd` is the wanted force, `f` the measured one, `ki` a gain. On a spring surface `f = ke * x` the force changes at `f_dot = ke * v`, so `f_dot = ke * ki * (fd - f)`. The gap to `fd` shrinks without overshoot, by about two thirds every `1 / (ke * ki)` seconds (the time constant). In steps of `dt` the gap is multiplied by `1 - ke * ki * dt`. Beyond 2 that flips sign and grows, so the loop is stable only while `ke * ki * dt < 2`.

A real task needs both laws, so the selection matrix `S` (on or off per axis) gives each axis exactly one: force law where `S = 1`, position law where `S = 0`.

![Hybrid position-force control](../assets/diagram-hybrid-selection.png)

*Position control along x, force control along y.*

![Hybrid control on a bumpy surface](../assets/fig-hybrid-bumpy.png)

*Left: the hybrid path follows the bumps. Right: force stays near 10 N instead of swinging between 0 and 20 N.*

## Build It

The hybrid law is one line over `v_pos` and `v_frc`, the two laws on every axis.

```python
v = (1 - S) * v_pos + S * v_frc
p = p + np.clip(v, -lim, lim) * dt
```

Assumptions: the tool tip tracks the commanded velocity exactly, the surface is a frictionless linear spring along x, and force is measured without noise or delay.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/02-force-and-hybrid-control -q
python3 phases/11-contact-and-manipulation/02-force-and-hybrid-control/code/main.py
```

## Use It

Repeat the press in MuJoCo with a soft-contact plane and compare the settled force with `ke * depth`.

Sources: Craig (chapter 11) and the original hybrid-control paper could not be opened (publisher page returned 403), so both are unchecked.

## Ship It

`outputs/skill-force-control-check.md` reviews a contact task for stiffness-sensitive commands and high loop gain.

## Exercises

1. Change `K_EST` to the true stiffness and show position control then hits 10 N, but only on that surface.
2. Find the largest `KI` that stays stable at `ke = 2.5e4` for `dt = 1 ms`.
3. Add 10 ms of delay to the force measurement and re-measure the stability limit.
