# Where M(q) Comes From: Deriving Arm Dynamics

> Learn where an arm's inertia numbers come from, so you can rebuild them when the robot changes.

**Type:** Build   **Prerequisites:** 02/03 Jacobians, 03/05 Computed Torque   **Time:** ~15 minutes

## In Plain Words

A two-link desk arm swings freely with no motor pushing. The swinging forearm tugs the upper arm along, so the two joints cannot be handled one at a time.

A step of calculus (in the fold) turns the arm's energy of motion into the inertia matrix and that tugging. A second method that adds up forces must give the same answer.

## Key Terms

- **Joint angles (`q`)**: how far each joint has turned.
- **Torque**: a twisting push, such as a motor's push on a joint.
- **Kinetic energy**: the energy something has because it is moving.
- **Inertia matrix (`M`)**: a table of four numbers saying how heavy the arm feels to each joint, and how the joints tug on each other.
- **Fast-motion torques (`h`)**: twisting pushes that appear when the arm moves fast, because how heavy it feels changes with its pose.
- **Lagrange equation**: a rule that turns the arm's energy of motion into joint torques (the maths is in the fold).

## The Problem

You bolt a heavier tool onto the arm, and the formulas for its inertia and swing forces no longer match. One mistyped sign and the program steering the arm works from the wrong arm model.

## The Concept

A controller is only as good as its arm model, so you must be able to rebuild it. Two independent ways give the same answer. One starts from the arm's energy of motion (calculus, in the fold). The other adds up forces link by link.

![Two roads, one torque](../assets/diagram-two-roads.png)

*Two roads to one torque. If they disagree, one has a bug.*

![Energy bars](../assets/clip-example.mp4)

*Compare the single-joint bars with the both-together bar. The difference is the tug.*

![Where the tugging torque comes from](../assets/diagram-energy-parts.png)

*The tugging exists because the inertia changes with the elbow.*

A free-swinging arm keeps its energy, so a flipped sign on `h` makes the energy drift.

![M and wrong-sign energy](../assets/fig-inertia-and-energy.png)

*Right: a flipped sign makes the energy wander.*

<details><summary>The math (optional)</summary>

Kinetic energy is `T = 1/2 qd' M(q) qd`, where `qd'` is the speed list `qd` written sideways; it expands to `1/2 (M11 qd1^2 + 2 M12 qd1 qd2 + M22 qd2^2)`; the Lagrange equation `tau = d/dt(dT/dqd) - dT/dq` gives `tau = M qdd + h`. For the lesson's arm (1 and 1.5 kg) at `q = (0.3, 1.0)` and 1 rad/s: joint 1 alone gives `T = 0.437`, `M11 = 0.873`; joint 2 alone `T = 0.0925`, `M22 = 0.185`; both `T = 0.836`, so `M12 = 0.307`. The wrong-sign energy wanders by tenths of a joule. The fast-motion torques `h` are called Coriolis and centripetal torques. `M` is built entry by entry: one joint at speed 1 and the others 0 gives `M11` or `M22`, both together give `M12`.

</details>

## Build It

Three short lines build `M` from the arm's energy, then form the torque.

```python
off = T(e0 + e1) - T(e0) - T(e1)          # unit velocities
M = [[2*T(e0), off], [off, 2*T(e1)]]
tau = M @ qdd + dMdt @ qd - dTdq          # dMdt, dTdq by central differences
```

`kinetic()` builds the energy; `lagrange_tau()` and `newton_euler()` are the two roads. Tests check the roads agree and a flipped sign fails the energy test.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/07-deriving-arm-dynamics -q
python3 phases/03-dynamics-and-control/07-deriving-arm-dynamics/code/figure.py
```

## Use It

MuJoCo computes the same matrix with `mj_fullM`; compare with `mass()`. Craig, Ch. 6.

Sources: [MuJoCo API reference](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html), checked 2026-11-10.

## Ship It

`outputs/skill-arm-dynamics-derivation-check.md` checks a dynamics model.

## Exercises

1. Double link 2's mass; which of `M`'s four numbers moves most?
2. Flip the sign of `h` and watch the energy test fail.
3. Add a small weight at the tip of link 2.
