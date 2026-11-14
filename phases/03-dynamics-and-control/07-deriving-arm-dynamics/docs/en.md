# Where M(q) Comes From: Deriving Arm Dynamics

> Write the arm's kinetic energy once, and differentiation hands you the inertia matrix and every Coriolis term.

**Type:** Build   **Prerequisites:** 02/03 Jacobians, 03/05 Computed Torque   **Time:** ~15 minutes

## In Plain Words

Picture a two-link bench arm swinging freely over a table with no motor pushing. The forearm's speed depends on both joints at once, so the energy of its motion, its kinetic energy, cannot be split joint by joint.

Adding up every link's kinetic energy and differentiating gives the inertia matrix and the coupling torques. A separate calculation adds up forces and moments instead. Both must give the same motor torques, and with no motor and no friction the arm's kinetic energy must stay constant.

## The Problem

Lesson 03/05 gave you `M(q)` (the inertia matrix) and `h(q, qd)` (the speed-dependent torques) and asked you to trust them. Change a link, add a joint, or mistype one sign, and the controller cancels the wrong arm. You cannot adapt a formula you cannot rebuild.

## The Concept

![Two roads, one torque](../assets/diagram-two-roads.png)

*Two independent derivations. If they disagree at any state, one of them has a bug.*

The kinetic energy of a horizontal arm is `T = 1/2 qd' M(q) qd`, (`qd'` is `qd` written sideways). Written out, `T = 1/2 (M11 qd1^2 + 2 M12 qd1 qd2 + M22 qd2^2)`, so one joint at unit speed shows `M11` or `M22`, and the cross term `M12` needs both moving. The Lagrange equation `tau = d/dt(dT/dqd) - dT/dq` then gives `tau = M qdd + h`.

Example: the lesson's arm (masses 1 and 1.5 kg) at `q = (0.3, 1.0)`. Joint 1 alone at 1 rad/s gives `T = 0.437`, so `M11 = 2T = 0.873`. Joint 2 alone gives `T = 0.0925`, so `M22 = 0.185`. Both together give `T = 0.836`. The extra `0.836 - 0.437 - 0.0925 = 0.307` is `M12`, the coupling.

![Energy bars](../assets/clip-example.mp4)

*Both joints turn at 1 rad/s. The stack is each joint's energy alone, the amber bar both together. The gap is `M12`, and it changes with the elbow angle.*

![Torque term sources](../assets/diagram-energy-parts.png)

*Coriolis and centripetal torques appear only because `M` changes with the elbow angle.*

The power `qd' h` need not vanish. It equals `1/2 qd' Mdot qd`, how fast the changing inertia alters kinetic energy, so in free motion `h` cancels it.

The other road is Newton-Euler. Walk outward computing each link's acceleration, then inward adding up forces and moments. It never touches energy.

![M and wrong-sign energy](../assets/fig-inertia-and-energy.png)

*Left: inertia against elbow angle for two link-2 masses. Right: with the correct `h`, free motion keeps kinetic energy constant; a flipped sign makes it wander by tenths of a joule.*

## Build It

```python
off = T(e0 + e1) - T(e0) - T(e1)          # unit velocities
M = [[2*T(e0), off], [off, 2*T(e1)]]
tau = M @ qdd + dMdt @ qd - dTdq          # dMdt, dTdq by central differences
```

`kinetic()` builds `T` from the link geometry. `lagrange_tau()` and `newton_euler()` are the two roads. Tests check that `M` is symmetric positive definite and matches lesson 03/05, that both roads agree at 20 random states, and that `energy_drift()` fails on a flipped sign.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/07-deriving-arm-dynamics -q
python3 phases/03-dynamics-and-control/07-deriving-arm-dynamics/code/figure.py
```

## Use It

MuJoCo computes the same `M` with `mj_fullM` and stores the bias force in `data.qfrc_bias`. Build the arm there and compare entries with `mass()`. Craig, Ch. 6, derives these equations for manipulators.

Sources: [MuJoCo API reference](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html), checked 2026-11-10.

## Ship It

`outputs/skill-arm-dynamics-derivation-check.md` checks a hand-derived or generated dynamics model with the two-road and energy tests.

## Exercises

1. Add the potential energy `V` of lesson 03/02 and extend `lagrange_tau`.
2. Make link 2 twice as heavy and predict which entry of `M` moves most.
3. Give link 2 a point mass at its tip and rebuild `kinetic()`.
