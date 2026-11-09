# DH Tables vs URDF Origins

> The same arm can be written as a DH table or as joint origins, and a table fed to the wrong DH convention returns a wrong pose without any error.

**Type:** Build   **Prerequisites:** 01/02 Forward Kinematics   **Time:** ~15 minutes

## The Problem

You copy a DH table from a textbook into your kinematics code. The zero pose looks right, so you move on. Weeks later the arm reaches the wrong point at every other pose, and nothing ever raised an error.

## The Concept

![One arm, three descriptions](../assets/diagram-three-ways.png)

*A DH table, a second DH table in the other convention, and URDF-style origins describe one arm and give one FK.*

Craig's convention (Ch. 3, Sec. 3.4) puts `a(i-1)` and `alpha(i-1)` on row `i`. The other common convention puts `a(i)` and `alpha(i)` there, so the same arm needs a table shifted by one row. A URDF-style joint says it more directly: an `xyz` offset and an `rpy` rotation from the parent, then a turn about the joint axis.

![Silent failure path](../assets/diagram-silent-wrong.png)

*Both conventions accept any four numbers per row. Neither can tell that the table belongs to the other.*

![Wrong convention against right](../assets/fig-wrong-convention.png)

*Left: one table, two routines, two arms. Right: the error is zero at the zero pose and grows from there.*

## Build It

Each routine multiplies four elementary transforms per row.

```python
def dh_craig(a, alpha, d, th):    return rx(alpha) @ tr(a,0,0) @ rz(th) @ tr(0,0,d)
def dh_standard(a, alpha, d, th): return rz(th) @ tr(0,0,d) @ tr(a,0,0) @ rx(alpha)
```

`craig_to_standard()` shifts `(a, alpha)` up one row and keeps the first pair as a base transform. `craig_to_urdf()` folds `d` into the origin, and raises if a theta offset would be dropped.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/01-dh-vs-urdf-origins -q
python3 phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/code/main.py
```

## Use It

A URDF loader or MuJoCo model reads origins, so a DH table from a datasheet must be converted before it is used there. Compare the converted model's tip pose with your DH code at five random poses, never only at zero.

## Ship It

`outputs/skill-dh-convention-check.md` is a checklist for any DH table you did not derive yourself.

## Exercises

1. Add a theta offset to `craig_to_urdf()` by converting `Rx(alpha) Rz(offset)` to roll, pitch and yaw.
2. Find a pose where the wrong convention happens to be right again, and explain why.
3. Write a check that detects a convention mismatch from two measured tip positions.
