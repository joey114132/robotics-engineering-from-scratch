# The Jacobian: Joint Speeds, Tip Speeds and Forces

> One matrix turns joint speeds into tip speed, and its transpose turns tip force into joint torque.

**Type:** Build   **Prerequisites:** 02/01 DH vs URDF Origins, 02/02 Inverse Kinematics   **Time:** ~15 minutes

## In Plain Words

Open a door by its handle. For the same hinge rotation, the handle travels farther than a point near the
hinge. A force on the door perpendicular to its face also produces more hinge torque when applied farther from
the hinge.

The Jacobian maps joint speeds to tip velocity at the arm's current pose. Its transpose maps a chosen tip
force to joint torque, so the speed and force calculations agree on power.

## The Problem

You want the tip to move in a straight line at 0.1 m/s, and the joints move at speeds that depend on the pose. You also want to know how hard each motor must push when the tip pushes on something. Both questions need the same matrix, and a Jacobian with one wrong sign passes every pose-only test.

## The Concept

![One matrix, used twice](../assets/diagram-bridge.png)

*Speeds go through J. Forces come back through the transpose of the same J.*

Column `j` of `J` is the tip velocity per unit speed of joint `j` (Craig, Ch. 5, Sec. 5.7). The same matrix gives the static relation `tau = J^T F` (Sec. 5.9 and 5.10). The reason is energy: power at the joints, `tau . qdot`, equals power at the tip, `F . v`.

![Two ways to build J](../assets/diagram-two-ways.png)

*An analytic J and a finite-difference J are built from the same FK. If they disagree, one has a bug.*

![Step size and velocity ellipses](../assets/fig-jacobian.png)

*Left: the finite-difference error has a minimum, with rounding noise below it and curvature above it. Right: unit joint speeds give a fat tip-speed ellipse when the arm is bent and a thin one when it is nearly straight.*

## Build It

Differentiate FK by hand, then nudge each joint and watch the tip.

```python
J = np.array([[-l1*s1 - l2*s12, -l2*s12], [l1*c1 + l2*c12, l2*c12]])
col = (fk(q + dq, L) - fk(q - dq, L)) / (2 * eps)   # one column per joint
```

Then `v = J @ qd` and `tau = J.T @ F`. A test holds a 2 kg mass at the tip and checks that `J.T` reproduces the point-mass gravity torque from the gravity-compensation lesson.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/03-jacobian-and-velocity -q
python3 phases/02-manipulator-kinematics/03-jacobian-and-velocity/code/main.py
```

## Use It

Physics engines and ROS 2 libraries return a Jacobian for a chosen point on the arm. Compare it with this one on a two-link model, and use the same finite-difference check on any Jacobian you did not write.

## Ship It

`outputs/skill-jacobian-check.md` is the finite-difference and power-balance check for any Jacobian.

## Exercises

1. Plot `|J q_dot|` for unit joint speeds against `q2` and find where it is smallest.
2. Add a third link and check that `J` has three columns that still match finite differences.
3. Show that the finite-difference step 1e-6 is also fine for `q` near 1000 rad, or find where it is not.
