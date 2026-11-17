# DH Tables vs URDF Origins

> Learn why a robot-arm table copied from a book can give wrong positions with no warning.

**Type:** Build   **Prerequisites:** 01/02 Forward Kinematics   **Time:** ~15 minutes

## In Plain Words

A DH table lists how each link of a bench arm sits on the one before it. Two conventions, meaning two rules for reading it, differ in order: slide then turn, or turn then slide.

With the elbow straight both readings put the hand in the same place. Bend the elbow and the hands part, with no error message.

## Key Terms

- **DH table**: a Denavit-Hartenberg table, one row of four numbers per joint, describing an arm.
- **Convention**: an agreed rule for reading a table; two conventions can read the same numbers differently.
- **Twist (`alpha`)**: how far the next joint axis tilts relative to this one.
- **Forward kinematics (FK)**: computing the hand's pose from the joint angles.
- **URDF origin**: in the robot file ROS reads, a joint's position (`xyz`) and rotation (`rpy`: roll, pitch, yaw) relative to its parent.
- **Zero pose**: the arm with every joint angle at 0.

## The Problem

You copy a robot arm's DH table, a table of numbers describing its links, from a textbook. The zero pose looks right, so you move on. Later the arm misses its target at most other poses, with no error.

## The Concept

The table decides where your code thinks the hand is. There are two ways to read it: slide along the link then turn, or turn then slide. With the elbow straight both give the same hand position, so the mistake hides.

![One arm, three descriptions](../assets/diagram-three-ways.png)

*Three descriptions of one arm should agree.*

![Silent failure path](../assets/diagram-silent-wrong.png)

*Any four numbers per row are accepted.*

![Wrong convention against right](../assets/fig-wrong-convention.png)

*Left: one table, two readings. Right: the error appears when the elbow bends.*

![Shoulder turn, then elbow bend](../assets/clip-example.mp4)

*Blue reads the table wrongly and drifts from green.*

<details><summary>The math (optional)</summary>

A row has four numbers: link length `a`, twist `alpha`, slide `d` and joint angle `theta`. Craig's convention (Ch. 3, Sec. 3.4) puts `a(i-1)` and `alpha(i-1)` on row `i`; the other puts `a(i)` and `alpha(i)` there. Example arm: 0.4 m and 0.3 m, Craig rows `(0, 0, 0, 0)` and `(0.4, 0, 0, 0)`. A 0.5 rad shoulder turn leaves the hands together; a 0.8 rad elbow bend parts them by 0.31 m.

</details>

## Build It

Each way of reading the table multiplies the same four moves in a different order.

```python
def dh_craig(a, alpha, d, th):    return rx(alpha) @ tr(a,0,0) @ rz(th) @ tr(0,0,d)
def dh_standard(a, alpha, d, th): return rz(th) @ tr(0,0,d) @ tr(a,0,0) @ rx(alpha)
```

`craig_to_standard()` shifts the numbers up one row, and `craig_to_urdf()` folds the slide into the robot file's offset and complains if a turn offset would be lost.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/01-dh-vs-urdf-origins -q
python3 phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/code/main.py
```

## Use It

A URDF loader or MuJoCo model reads offsets, so convert a datasheet's DH table first, then compare the hand position at five random poses.

## Ship It

`outputs/skill-dh-convention-check.md` checks any DH table you did not derive.

## Exercises

1. Bend the elbow in the demo and watch the two readings part.
2. Find a pose where the wrong reading is right anyway.
3. Detect a mismatch from two measured hand positions.
