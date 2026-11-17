# Euler Angles and Gimbal Lock

> Learn why roll, pitch and yaw numbers suddenly jump when a tool tilts straight down.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3), 01/03 Axis-Angle and Quaternions   **Time:** ~15 minutes

## In Plain Words

A camera sits in three nested rings (a gimbal, like a gyroscope toy). One ring turns it about the vertical, one tilts it, one rolls it about its viewing line. Tilted straight down, two rings spin the view about the same line, so a direction is gone.

Near that pose, two different ring settings make the same view. Code reading the angles picks one, so yaw and roll jump.

## Key Terms

- **Euler angles**: three turns applied in a fixed order, named roll, pitch and yaw.
- **Roll, pitch, yaw**: turns about the forward axis, the side axis and the vertical axis.
- **Gimbal**: three nested rings that let something turn in any direction.
- **Gimbal lock**: a pose where two rings line up and one direction of turning is lost.
- **Euler rates**: how fast each ring is turning.

## The Problem

A camera on a robot reports three angles, roll, pitch and yaw. As it tilts through straight down, two of the numbers suddenly jump, or the arm's control program asks for impossibly fast joint spins.

## The Concept

Many robot sensors report orientation as three angles, and near one pose those numbers stop making sense. Picture three rings, as in the first diagram; looking straight down, two line up.

![Rings lose a direction](../assets/diagram-gimbal-rings.png)

*Straight down, two rings line up and a direction is lost.*

![Two rigs, one pose](../assets/clip-example.mp4)

*Two different ring settings, one identical view.*

The code that reads the angles back must pick one of the two settings, and it switches as the camera passes through, so the numbers jump. To turn smoothly near straight down, the rings would have to spin faster and faster.

![Smooth turn, jump](../assets/diagram-angle-jump.png)

*The camera turns smoothly; roll and yaw flip straight down.*

![Jump and rate blow-up](../assets/fig-gimbal-lock.png)

*Near straight down, the needed ring speeds shoot up.*

<details><summary>The math (optional)</summary>

At pitch 90 degrees roll `+a` equals yaw `-a`, so only `yaw - roll` matters. Reading angles back gives pitch between -90 and 90 degrees, so past 90 it switches to a second spelling with roll and yaw 180 degrees away. The rate matrix has determinant `cos(pitch)` (one number that is 0 when the matrix loses a direction), which is 0 at 90 degrees. The plot sweeps pitch from 60 to 120 degrees; for a 1 rad/s spin at yaw 0 the rates grow like 1 / cos(pitch). The clip turns the roll ring +1.2 rad and the yaw ring -1.2 rad. `locked=True` is reported within 1e-9 of the lock.

</details>

## Build It

`euler_to_R` builds a rotation from three angles. `R_to_euler()` reads them back and reports `locked=True` near the lock, and `euler_rates()` refuses to run there.

```python
def euler_to_R(roll, pitch, yaw):
    return _rot(2, yaw) @ _rot(1, pitch) @ _rot(0, roll)
```

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/05-euler-angles-and-gimbal-lock -q
python3 phases/01-math-foundations/05-euler-angles-and-gimbal-lock/code/main.py
```

## Use It

Compare `R_to_euler()` with SciPy's `as_euler` (a Python add-on). SciPy warns at the lock, so compare rotations.

## Ship It

`outputs/skill-euler-angle-audit.md` checks for Euler angles in control and logging.

## Exercises

1. Tilt the camera to 89, then 90 degrees.
2. At pitch 90, try another roll and yaw and check with `euler_to_R` that the rotation is the same.
3. Compare averaging the three angles with the smooth turn (slerp) from lesson 01/03.
