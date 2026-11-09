# Inverse Kinematics of a Two-Link Arm

> Reaching a point is a triangle with two valid answers and a hard edge, and the only honest test is to run FK on the answer.

**Type:** Build   **Prerequisites:** 01/02 Forward Kinematics, 02/01 DH vs URDF Origins   **Time:** ~15 minutes

## The Problem

You ask the arm to touch a point and `acos` returns `nan`, or the arm folds the wrong way and hits the table. A target slightly past full stretch is easy to produce, and a solver that hides it moves the arm somewhere you did not ask for.

## The Concept

![IK as a triangle](../assets/diagram-triangle.png)

*The base, the elbow and the target form a triangle with sides L1, L2 and r. The law of cosines gives q2 up to a sign.*

The sign is the elbow. One target has two arms that reach it, and at full stretch they merge into one (Craig, Ch. 4, on solvability and on algebraic against geometric solutions).

![Reach check and FK check](../assets/diagram-decision.png)

*Targets outside the band from `|L1 - L2|` to `L1 + L2` are refused. Every answer is confirmed by FK.*

![Two elbows and the reach limit](../assets/fig-two-elbows.png)

*Left: both arms touch the target. Right: sliding the target outward, the two branches meet at the edge and then no answer exists.*

## Build It

Law of cosines first, then the angle to the target minus the angle inside the triangle.

```python
c2 = (x*x + y*y - l1*l1 - l2*l2) / (2*l1*l2)
if abs(c2) > 1 + tol: raise ValueError("unreachable")
s2 = np.sqrt(1 - c2*c2) * (1 if elbow == "down" else -1)
q2 = np.arctan2(s2, c2)
q1 = np.arctan2(y, x) - np.arctan2(l2*s2, l1 + l2*c2)
```

A small tolerance keeps rounding noise at the boundary from becoming a false refusal. The tests run `fk(ik(p))` on 200 targets per branch.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/02-inverse-kinematics-2link -q
python3 phases/02-manipulator-kinematics/02-inverse-kinematics-2link/code/main.py
```

## Use It

Arms with more joints use a numerical solver. Compare against this closed form on a two-link model, and check that the solver also reports an unreachable target instead of returning its best guess.

## Ship It

`outputs/skill-ik-answer-check.md` is the check every IK answer must pass before it reaches a controller.

## Exercises

1. Add a joint limit `|q2| < 2.8` and make `ik` pick the other elbow when one is out of range.
2. Plot the whole reachable band as a heat map of the number of valid answers.
3. Show what happens to `q1` when `L1 = L2` and the target is the base.
