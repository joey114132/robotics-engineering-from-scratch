# The Jacobian: Joint Speeds, Tip Speeds and Forces

> Learn how joint speeds set the hand's speed, and how a push on the hand turns into motor torque.

**Type:** Build   **Prerequisites:** 02/01 DH vs URDF Origins, 02/02 Inverse Kinematics   **Time:** ~15 minutes

## In Plain Words

Turn a desk arm's shoulder steadily and the tip swings around it, faster the farther it is from the shoulder. So the tip's speed and direction depend on the pose.

The Jacobian is a table for the current pose: feed it joint speeds, get the tip's motion. Flip it on its side and it turns a push on the tip into the twist each motor must supply.

## Key Terms

- **Jacobian (`J`)**: a table of numbers that turns joint speeds into the tip's speed and direction for the current pose.
- **Tip**: the end of the arm, where the hand or tool sits.
- **Torque (`tau`)**: a twisting force, such as a motor's push on a joint.
- **Transpose (`J^T`)**: the same matrix with its rows and columns swapped.
- **Finite difference**: estimating a slope by nudging an input a small step and watching the output.

## The Problem

You want a robot arm's hand to move straight, and to know how hard each motor must push when the hand presses on something. Both need one table of numbers, and a wrong sign in it would not show in a test that only checks positions.

## The Concept

To move a hand straight or press on a table, each joint needs the right speed and force. The Jacobian, recalculated for each pose, turns joint speeds into hand speed. Flipped on its side, it turns a push on the hand into the push each motor must make.

![One matrix, used twice](../assets/diagram-bridge.png)

*Speeds go through the table; forces come back through the flipped table.*

![Two ways to build J](../assets/diagram-two-ways.png)

*Two ways to build it must agree.*

![Which hand motions are easy: bent arm and straight arm](../assets/fig-jacobian.png)

*A bent arm moves its hand easily in every direction. A straight arm cannot: one direction is hard.*

![Torque while stretching](../assets/clip-example.mp4)

*The stretched arm needs far more shoulder torque.*

<details><summary>The math (optional)</summary>

`v = J @ qd` and `tau = J^T F` (Craig, Ch. 5, Sec. 5.7, 5.9, 5.10). Tip power `F . (J q-dot)` equals joint power `tau . q-dot`. A 2 kg block gives `F = 2 * 9.81 = 19.6` N. Stretched flat the tip is 0.9 m out and the shoulder needs 19.6 x 0.9 = 17.7 N m; nearly over the base it needs about 1 N m. The step size has a best value between rounding noise and curvature. The clip draws 0.03 m of bar per N m. The straight move is 0.1 m/s.

</details>

## Build It

Two ways to build the table: a formula, and nudging each joint a little and watching the hand.

```python
J = np.array([[-l1*s1 - l2*s12, -l2*s12], [l1*c1 + l2*c12, l2*c12]])
col = (fk(q + dq, L) - fk(q - dq, L)) / (2 * eps)   # one column per joint
```

Then speeds go through `J @ qd` (`qd`: the joint speeds) and forces through `J.T @ F` (`F`: the push on the tip).

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/03-jacobian-and-velocity -q
python3 phases/02-manipulator-kinematics/03-jacobian-and-velocity/code/main.py
```

## Use It

Physics engines and ROS 2 libraries return Jacobians; compare one on a two-link arm.

## Ship It

`outputs/skill-jacobian-check.md` is a finite-difference and power-balance check.

## Exercises

1. Compare the two builds at a few poses.
2. Hang a heavier block.
3. Straighten the arm; easy directions shrink.
