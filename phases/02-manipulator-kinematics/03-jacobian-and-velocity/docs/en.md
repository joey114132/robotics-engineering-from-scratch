# The Jacobian: Joint Speeds, Tip Speeds and Forces

> Learn how joint speeds set the hand's speed, and how a push on the hand turns into motor torque.

**Type:** Build   **Prerequisites:** 02/01 DH vs URDF Origins, 02/02 Inverse Kinematics   **Time:** ~15 minutes

## In Plain Words

Turn a bench arm's shoulder steadily and the tip swings around it, faster the farther it is from the shoulder, so the tip's velocity depends on the pose.

The Jacobian tabulates this for the current pose: joint speeds in, tip velocity out. Its transpose turns a push on the tip into the torque each motor needs to resist it.

## Key Terms

- **Jacobian (`J`)**: a matrix that turns joint speeds into tip velocity for the current pose.
- **Tip**: the end of the arm, where the hand or tool sits.
- **Torque (`tau`)**: a twisting force, such as a motor's push on a joint.
- **Transpose (`J^T`)**: the same matrix with its rows and columns swapped.
- **Finite difference**: estimating a slope by nudging an input a small step and watching the output.
- **Dot product (`.`)**: multiply matching entries of two lists and add them up.

## The Problem

You want a robot arm's tip to move straight at 0.1 m/s, and to know each motor's push when the tip presses on something. One wrong sign in the Jacobian passes every position-only test.

## The Concept

To move a hand straight or press on a table, each joint needs the right speed and force.

`J` works both ways: `q-dot` joint speeds, `v` tip speed, `F` tip force, `tau` motor torques.

![One matrix, used twice](../assets/diagram-bridge.png)

*Speeds go through J. Forces come back through its transpose.*

Column `j` of `J` is the tip velocity when only joint `j` turns at unit speed (Craig, Ch. 5, Sec. 5.7). Tip power `F . (J q-dot)` must equal joint power `tau . q-dot`, which gives `tau = J^T F` (Sec. 5.9 and 5.10).

![Two ways to build J](../assets/diagram-two-ways.png)

*By hand or by finite differences, both start from FK. If they disagree, one has a bug.*

![Step size and velocity ellipses](../assets/fig-jacobian.png)

*Left: step-size error has a minimum. Right: tip-speed ellipses, fat for a bent arm, thin when nearly straight.*

A 2 kg block hangs at the tip, so `F = 2 * 9.81 = 19.6` N. Stretched flat, the tip is 0.9 m out and the shoulder needs 19.6 x 0.9 = 17.7 N m; with the tip nearly over the base, `tau = J^T F` gives about 1 N m.

![Torque while stretching](../assets/clip-example.mp4)

*Red arrow: `F`. Amber bars: `|tau|`, 0.03 m tall per N m.*

## Build It

Two ways to build `J`:

```python
J = np.array([[-l1*s1 - l2*s12, -l2*s12], [l1*c1 + l2*c12, l2*c12]])
col = (fk(q + dq, L) - fk(q - dq, L)) / (2 * eps)   # one column per joint
```

Then `v = J @ qd` and `tau = J.T @ F`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/03-jacobian-and-velocity -q
python3 phases/02-manipulator-kinematics/03-jacobian-and-velocity/code/main.py
```

## Use It

Physics engines and ROS 2 libraries return Jacobians; compare one with this on a two-link model.

## Ship It

`outputs/skill-jacobian-check.md` is a finite-difference and power-balance check.

## Exercises

1. Plot `|J q_dot|` for unit joint speeds against `q2`.
2. Add a third link and check `J` still matches finite differences.
3. Check the step 1e-6 for `q` near 1000 rad.
