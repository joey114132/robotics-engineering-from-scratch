# Euler Angles and Gimbal Lock

> Roll, pitch and yaw are three numbers in a fixed order, and near pitch 90 degrees that order has a hole.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3), 01/03 Axis-Angle and Quaternions   **Time:** ~15 minutes

## In Plain Words

Point a phone camera straight upward. Turning around the room's vertical axis and twisting about the camera's
forward axis now turn about the same line. Those controls can no longer describe independent changes of
direction.

Euler angles meet this problem when pitch reaches vertical: roll and yaw become coupled. Nearby, a modest
physical turn can require very large changes in the reported angles. Crossing that pose can also make the
angle readings jump while the phone moves smoothly.

## The Problem

A wrist or camera reports roll, pitch and yaw. As the tool tilts up through vertical, roll and yaw suddenly jump by 180 degrees, or the controller asks for huge joint speeds. The sensor is fine. The angle format is the problem.

## The Concept

![Three nested rings lose one degree of freedom](../assets/diagram-gimbal-rings.png)

*Yaw, pitch and roll are three rings. At pitch 90 degrees the roll ring lines up with the yaw ring and the pair turns the same way.*

![A smooth turn reads as a jump](../assets/diagram-angle-jump.png)

*Every orientation has two spellings. Across 90 degrees the reader switches spelling, so roll and yaw flip by 180 degrees while the tool moves smoothly.*

We use ZYX order, `R = Rz(yaw) Ry(pitch) Rx(roll)`. The map from Euler rates to world angular velocity is a 3x3 matrix `E` with `det E = cos(pitch)`. At 90 degrees it has rank 2, so some spins have no Euler rates at all.

![Jump and rate blow-up](../assets/fig-gimbal-lock.png)

*Left: a pure pitch sweep from 60 to 120 degrees. Roll and yaw jump by 180 degrees at 90. Right: for a 1 rad/s world-x spin at yaw 0, the Euler rate norm grows like 1 / cos(pitch).*

## Build It

```python
def euler_to_R(roll, pitch, yaw):
    return _rot(2, yaw) @ _rot(1, pitch) @ _rot(0, roll)
```

`R_to_euler()` reads pitch from `-R[2, 0]`, then roll and yaw from the other entries. When `|R[2, 0]|` is within 1e-9 of 1 it returns `locked=True` and sets roll to 0, because only `yaw - roll` at pitch +90 degrees or `yaw + roll` at -90 degrees is defined. `other_spelling()` returns the second triple for the same rotation. `euler_rates()` solves with `E` and raises at gimbal lock.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/05-euler-angles-and-gimbal-lock -q
python3 phases/01-math-foundations/05-euler-angles-and-gimbal-lock/code/main.py
```

## Use It

Compare `R_to_euler()` with `scipy.spatial.transform.Rotation.as_euler("ZYX")`. SciPy reports gimbal lock with a warning, so check that both give the same rotation, not the same angles.

## Ship It

`outputs/skill-euler-angle-audit.md` checks a system for Euler angles in control, logging and filters.

## Exercises

1. Find a second `(roll, yaw)` pair with the same `R` at pitch 90 degrees.
2. At yaw 0 and pitch 89.9 degrees, compute `E` and the largest Euler rate for a 1 rad/s world-x spin.
3. Smooth the angles with a low-pass filter across the jump, then smooth `R` with a slerp, and compare.
