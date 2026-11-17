# Axis-Angle and Quaternions

> Learn why a robot wrist can spin a whole turn the long way round, and the one-line check that stops it.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3)   **Time:** ~15 minutes

## In Plain Words

A robot wrist is told to turn a tiny bit left. Turning almost a full circle right reaches the same direction. A quaternion names an orientation, but q and its opposite, -q, name the same one, so a smooth turn between two orientations flips the sign when needed to keep the turn short.

## Key Terms

- **Quaternion**: four numbers that name an orientation; a unit quaternion has length one.
- **Axis-angle**: a rotation given as a line to turn about plus an angle.
- **Slerp**: a smooth, even-speed turn between two orientations.
- **Interpolator**: code that moves smoothly between a start value and a target value.
- **Dot product**: multiply matching entries of two lists and add them up; it scores how alike two quaternions are.
- **Radian (rad)**: an angle unit where one full turn is about 6.28.

## The Problem

A robot wrist, told to correct a tiny error, spins almost a full turn the long way round. The target arrived with a flipped sign and the code trusted it.

## The Concept

Robots glide smoothly between orientations all the time, and one sign slip makes the wrist take the long way.

![Two wrists, one pose](../assets/clip-example.mp4)

*Same final pose. Green turned one extra full turn.*

A quaternion is four numbers that name an orientation, and every orientation has two of them, one the negative of the other.

![q and -q](../assets/diagram-double-cover.png)

*Two opposite points on the sphere mean the same turn.*

The fix: check whether the target is on the far side, and if so flip its sign before gliding.

![Slerp sign check](../assets/diagram-slerp-sign-fix.png)

*If the check says far, flip the sign, and the short way is taken.*

![Swept angle](../assets/fig-slerp-long-way.png)

*Without the fix the wrist sweeps almost a full turn. With it, a small one.*

<details><summary>The math (optional)</summary>

A turn of angle `t` about axis `k` is the quaternion `(cos(t/2), sin(t/2) k)`. A turn of 0.1 about z gives `q = (0.9988, 0, 0, 0.0500)`; adding a full turn (`t = 0.1 + 2pi`) gives `-q = (-0.9988, 0, 0, -0.0500)`. The dot product of `q0 = (1, 0, 0, 0)` and `-q` is -0.9988: negative means far, so flip. Without the fix the wrist sweeps 354.3 degrees; with it 5.7 (0.1 rad). The clip's needles show half angles 0.05 and pi + 0.05.

</details>

## Build It

`rodrigues` turns an axis and an angle into a rotation matrix. `slerp` glides between two orientations, and its `fix` option flips the sign when the dot product is negative.

```python
def rodrigues(axis, angle):
    k = _unit(axis)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * K @ K

def slerp(q0, q1, t, fix=True):
    d = float(q0 @ q1)
    if fix and d < 0:
        q1, d = -q1, -d
    om = np.arccos(min(d, 1.0))
    return (np.sin((1 - t) * om) * q0 + np.sin(t * om) * q1) / np.sin(om)
```

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/03-axis-angle-and-quaternions -q
```

## Use It

SciPy's `Rotation.from_quat` and `Slerp` do this. SciPy writes the plain number last and this lesson writes it first, so check the order when you cross a library boundary.

Sources: Craig, *Introduction to Robotics*, 3rd ed., ch. 2 (Euler parameters; section number not verified).

## Ship It

`outputs/skill-quaternion-sign-check.md` reviews code that interpolates orientations.

## Exercises

1. Run `slerp` with `fix=False` and watch the long way.
2. Negate a quaternion and check that it gives the same rotation matrix.
3. Find the target angle where the sign check first flips.
