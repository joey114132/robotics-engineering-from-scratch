# Axis-Angle and Quaternions

> Every rotation has two quaternions, and an interpolator that ignores this can spin a wrist a full turn.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3)   **Time:** ~15 minutes

## In Plain Words

A clock hand sits just past the top. You can reach it with a short clockwise turn or an almost complete
counterclockwise turn. The destination alone does not choose the route.

With quaternions, q and -q describe the same orientation. Interpolating toward the opposite sign can send a
wrist the long way around. Slerp checks the dot product and flips the target sign when needed, keeping the
orientation while choosing the shorter rotation.

## The Problem

A wrist was told to correct a 0.1 rad error and instead spun almost a full turn the long way round. The target quaternion had arrived with the opposite sign, which names the same orientation. The interpolator trusted the sign and took the far side.

## The Concept

![q and minus q are one rotation](../assets/diagram-double-cover.png)

*Two opposite points on the 4D unit sphere map to one 3x3 rotation matrix.*

Rodrigues' formula turns an axis `k` and an angle into a matrix: `R = I + sin(t) K + (1 - cos(t)) K^2`, where `K` is the cross-product matrix of `k`. A unit quaternion is `(cos(t/2), sin(t/2) k)`. Because `t` and `t + 2pi` give `q` and `-q`, each rotation has two quaternions (a double cover).

![Slerp checks the sign of the dot product](../assets/diagram-slerp-sign-fix.png)

*If `dot(q0, q1)` is negative, negate `q1` before interpolating. The rotation is unchanged and the short arc is taken.*

![Swept angle with and without the fix](../assets/fig-slerp-long-way.png)

*Same start, same target. Without the fix the wrist sweeps 354.3 degrees, with it 5.7 degrees.*

## Build It

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

The full file adds `quat_mul`, `quat_to_R` and `R_to_quat`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/03-axis-angle-and-quaternions -q
```

## Use It

SciPy's `Rotation.from_quat` and `Slerp` do this. SciPy stores quaternions scalar-last, `(x, y, z, w)`, and the last test checks that against this lesson's scalar-first `(w, x, y, z)`. Always confirm the order when you cross a library boundary.

Sources: Craig, *Introduction to Robotics*, 3rd ed., ch. 2 (Euler parameters; section number not verified).

## Ship It

`outputs/skill-quaternion-sign-check.md` reviews any code that interpolates or compares orientations.

## Exercises

1. Show that `quat_mul(q, q_inv)` is the identity, with `q_inv = (w, -x, -y, -z)`.
2. For a start of 0 rad about z, find the target angle where `dot` crosses zero.
3. Compare the angle `2*arccos(|dot|)` with the path angle, with and without the fix.
