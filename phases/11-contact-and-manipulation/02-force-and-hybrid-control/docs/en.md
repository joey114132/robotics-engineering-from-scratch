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

Picture a robot told to press a sponge with a steady force. It guesses how soft the sponge is and presses to a fixed depth. If the sponge is stiffer than guessed, it pushes far too hard.

![Three arms](../assets/clip-example.mp4)

*Same depth on three sponges: very different forces.*

## The Concept

A robot wiping or sanding needs a steady force, not a steady position.

Force control skips the guess: the robot measures the push. If it is weak, the tool goes deeper; if it is strong, it backs off.

![Position miss](../assets/diagram-position-miss.png)

*The command is right only for the guessed stiffness.*

![Force vs stiffness](../assets/fig-force-vs-stiffness.png)

*Force control reaches the target on every surface.*

Real tasks need both: slide along the surface by position, press into it by force. That is hybrid control.

![Selection](../assets/diagram-hybrid-selection.png)

*Position along x, force along y.*

![Bumpy surface](../assets/fig-hybrid-bumpy.png)

*The path follows the bumps and the force stays steady.*

<details><summary>The math (optional)</summary>

Pressing with 10 N, the robot assumes 5000 N/m and commands a 2 mm squeeze, but the sponge top sits 0.4 mm lower, so only 1.6 mm gets squeezed. Then 1000 N/m gives 1.6 N, 5000 N/m gives 8 N, 25000 N/m gives 40 N. The force loop moves the tool tip at `v = ki * (fd - f)`, with `fd` the wanted force and `f` the measured one. On a spring surface `f = ke * x` the gap shrinks by about two thirds every `1 / (ke * ki)` seconds, so a stiffer surface settles faster. Each step of `dt` multiplies the gap by `1 - ke * ki * dt`, so it is stable only while `ke * ki * dt < 2`: a loop that works on a soft pad can shake on steel. The selection matrix `S` gives each axis one law; `S = diag(0, 1)` means position on x and force on y.

</details>

## Build It

The hybrid law mixes the velocities of the two laws.

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

Repeat the press in MuJoCo and compare the settled force with stiffness times depth.

Sources: Craig (chapter 11) and the original hybrid-control paper could not be opened (403); both unchecked.

## Ship It

`outputs/skill-force-control-check.md` reviews a contact task for stiffness-sensitive commands and high gain.

## Exercises

1. Tell the robot the true stiffness; position control then works, but only on that surface.
2. Raise the loop gain until the force starts to shake.
3. Add a small delay to the force reading and see the safe gain shrink.
