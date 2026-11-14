# Rotations and SE(3)

> A pose is a rotation and a position, and the order you multiply them in decides the result.

**Type:** Build   **Prerequisites:** none   **Time:** ~15 minutes

## In Plain Words

Hold a drone, nose to the door. Roll it a quarter turn about its nose, then spin it a quarter turn about the vertical line: the nose points left. Spin first, then roll about the door line: the nose swings up to the ceiling.

The first turn moved the drone, so the second acts on a drone that faces differently. Position works the same way: shift before turning and the turn carries the drone around the origin. A pose is orientation plus position, and multiplying poses in order tracks both.

## The Problem

A camera sees a cup at (0.2, 0, 0.5) in its own frame (x, y, z measured from the camera), and the arm needs it in the base frame, measured from its base. Multiply the camera's and the cup's transforms in the wrong order and the result is still a valid-looking pose, just a wrong one, so the arm reaches for a point that does not exist and nothing complains.

## The Concept

A rotation matrix `R` turns without stretching or mirroring: its columns are perpendicular and one unit long (orthonormal) and its determinant, a mirror check, is +1 (a mirror gives -1). A rigid transform `T` stacks `R` and a position `p` into one 4x4 matrix, a pose in SE(3). Applying `T` to a point turns it by `R`, then shifts it by `p`. In a product `A @ B` the right matrix acts first, so order matters.

![A transform and its inverse](../assets/diagram-transform-chain.png)

*Follow the numbers: `T_base_cam` maps camera coordinates to base coordinates, and its inverse maps back.*

A drone's pose is a quarter turn about z plus a shift `p = (1, 2, 0)`. Turn then shift: its centre ends at `p` and a mark on its nose, (1, 0, 0), at (1, 3, 0). Shift then turn: the turn swings the centre around the origin to (-2, 1, 0) and the nose mark to (-2, 2, 0).

![Two drones, opposite orders](../assets/clip-example.mp4)

*Green turns, then moves onto the grey target. Blue moves first, so the turn swings it around the origin.*

![Two turn orders](../assets/diagram-rotation-order.png)

*Compare the rows: roll about x then spin about z, or the reverse, sends the nose (1, 0, 0) to (0, 1, 0) or (0, 0, 1).*

The inverse has a closed form, `[R^T, -R^T p]`: `R^T` (rows and columns of `R` swapped) undoes the turn, so `T^-1` shifts back, then turns back. A general inverse hides drift, the slow error from many rounded multiplications, by silently inverting a slightly wrong `R`. The closed form trusts `R^T` to undo `R`, so drift makes `T^-1 T` miss the identity.

![Float32 drift with and without repair](../assets/fig-rotation-drift.png)

*Compare the curves. Composing 20,000 small rotations in float32 (rounded numbers) lets drift grow. Snapping `R` back (`reorthonormalize`) every 100 steps keeps it at rounding level.*

## Build It

```python
def is_rotation(R, tol=1e-9):
    return np.allclose(R.T @ R, np.eye(3), atol=tol) and np.isclose(np.linalg.det(R), 1.0, atol=tol)

def invert_T(T):
    R, p = T[:3, :3], T[:3, 3]
    return make_T(R.T, -R.T @ p)

def reorthonormalize(R):
    U, _, Vt = np.linalg.svd(R)
    return U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
```

Helpers `rot_x`, `rot_y`, `rot_z`, `make_T`: see `code/main.py`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/01-rotations-and-se3 -q
```

## Use It

`scipy.spatial.transform.Rotation` does all of this; the last test compares it with `rot_z(0.8)`.

Sources: Craig, *Introduction to Robotics*, 3rd ed., ch. 2 (descriptions and transformations).

## Ship It

`outputs/skill-transform-sanity.md` is a checklist that catches these pose bugs before hardware.

## Exercises

1. Compose `rot_x(a)` and `rot_z(b)` both ways and print the tip difference.
2. Reproduce the drift curve in float64. How many steps until `is_rotation` fails?
3. Write `compose(Ts)` that multiplies a list of transforms and checks the result.
