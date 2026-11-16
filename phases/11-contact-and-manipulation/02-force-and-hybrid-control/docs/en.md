# Force and Hybrid Control

> Learn how a robot presses with the right force on a surface of unknown softness.

**Type:** Build   **Prerequisites:** 11/01 Contact Models   **Time:** ~15 minutes

## In Plain Words

Wiping a desk means moving a sponge across it while pressing down. Pushing to a fixed depth gives a different force on a softer sponge.

Force control measures the push, going deeper when it is weak and backing off when it is strong. Hybrid control gives the sliding direction a position target and the pressing direction a force target.

## Key Terms

- **Force control**: moving the tool according to the measured force, not a planned position.
- **Hybrid control**: position control on some axes and force control on the others.
- **Stiffness (`ke`)**: the newtons a surface pushes back per metre squeezed.
- **Gain (`ki`)**: the factor that turns a force error into a tool speed.
- **Time constant**: the time in which an error shrinks by about two thirds.
- **Selection matrix (`S`)**: a switch per axis choosing force law or position law.

## The Problem

Picture a robot told to press a sponge with 10 N. It assumes 5000 N/m and commands a 2 mm squeeze, but the sponge top sits 0.4 mm lower, so only 1.6 mm gets squeezed. Then 1000 N/m gives 1.6 N, 5000 N/m 8 N, 25000 N/m 40 N.

![Three arms](../assets/clip-example.mp4)

*Red bars: force, 1.6 cm per N.*

## The Concept

A real robot wiping or sanding needs a steady force, not a steady position.

![Position miss](../assets/diagram-position-miss.png)

*The command is right only for the assumed stiffness.*

![Force vs stiffness](../assets/fig-force-vs-stiffness.png)

*Left: the force loop reaches 10 N everywhere. Right: position force grows with stiffness.*

The force loop moves the tool tip at `v = ki * (fd - f)`, with `fd` the wanted force and `f` the measured one. On a spring surface `f = ke * x`, so the force gap shrinks without overshoot, by about two thirds every `1 / (ke * ki)` seconds. Each step of `dt` multiplies the gap by `1 - ke * ki * dt`, so it is stable only while `ke * ki * dt < 2`.

The selection matrix `S` gives each axis one law: force where `S = 1`, position where `S = 0`.

![Selection](../assets/diagram-hybrid-selection.png)

*Position along x, force along y.*

![Bumpy surface](../assets/fig-hybrid-bumpy.png)

*Left: the path follows the bumps. Right: force stays near 10 N, not 0 to 20 N.*

## Build It

The hybrid law mixes `v_pos` and `v_frc`, the two laws' velocities.

```python
v = (1 - S) * v_pos + S * v_frc
p = p + np.clip(v, -lim, lim) * dt
```

Assumptions: exact velocity tracking, a frictionless linear spring, noise-free force.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/02-force-and-hybrid-control -q
python3 phases/11-contact-and-manipulation/02-force-and-hybrid-control/code/main.py
```

## Use It

Repeat the press in MuJoCo; compare the force with `ke * depth`.

Sources: Craig (chapter 11) and the original hybrid-control paper could not be opened (403); both unchecked.

## Ship It

`outputs/skill-force-control-check.md` reviews a contact task for stiffness-sensitive commands and high gain.

## Exercises

1. Set `K_EST` to the true stiffness; position control hits 10 N, but only on that surface.
2. Find the largest `KI` stable at `ke = 2.5e4` for `dt = 1 ms`.
3. Add 10 ms of force-measurement delay; re-measure the limit.
