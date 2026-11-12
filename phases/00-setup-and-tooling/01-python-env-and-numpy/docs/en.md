# Python Env and numpy

> numpy never checks units or shapes for you, so a robot program has to check them itself.

**Type:** Build   **Prerequisites:** none   **Time:** ~15 minutes

## In Plain Words

A recipe says to add a spoonful of salt, but you read the amount as a cupful. The written amount has not
changed; changing the unit changes what goes into the soup.

Robot data can fail the same way. An angle in degrees means something different when read as radians. Arrays
also need agreed shapes so each value keeps its intended role. Checking units and shapes catches mistakes that
ordinary arithmetic accepts.

## The Problem

An encoder driver reports a joint at `90`. You pass it to `np.cos`, and the link tip lands 0.45 of a link length away from where it should be, with no error and no warning. numpy treats every number as radians and every array as just numbers, so a unit mistake or a transposed array looks exactly like a correct run.

## The Concept

![Degrees fed to np.cos](../assets/diagram-degrees-bug.png)

*The sensor says 90 degrees, `np.cos` reads 90 radians. A guard at the boundary turns the silent error into a loud one.*

Robot data has two things numpy cannot see: a unit (radians, metres) and a meaning for each axis. We store points as rows, shape `(N, 3)`, so a rotation is applied as `points @ R.T`.

![Points are rows](../assets/diagram-shape-flow.png)

*Forgetting `.T` does not crash. It rotates the points the other way.*

![Wrong unit, wild answer](../assets/fig-degrees-vs-radians.png)

*Same readings, two interpretations. The wrong one swings the tip of a 0.4 m link by almost 0.8 m.*

## Build It

Three small guards. Each one fails with a message that names the argument.

```python
def check_shape(x, shape, name="array"):
    a = np.asarray(x, dtype=float)
    if a.ndim != len(shape) or any(s is not None and s != n for s, n in zip(shape, a.shape)):
        raise ValueError(f"{name}: expected shape {shape}, got {a.shape}")
    return a

def looks_like_degrees(q, limit=2 * np.pi):
    return bool(np.max(np.abs(q)) > limit)
```

`joint_angles(q)` calls both and refuses a vector that looks like degrees. `rotate_z(points, theta)` checks `(N, 3)` first. A continuous joint can pass `2 * pi`, so raise `limit` for those joints.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-setup-and-tooling/01-python-env-and-numpy -q
python3 phases/00-setup-and-tooling/01-python-env-and-numpy/code/main.py
```

## Use It

Create the environment with `python3 -m venv .venv`, the command and directory name the Python venv page documents. The rest is this lesson's own advice: one environment per project, versions recorded with `pip freeze`, `np.testing.assert_allclose` in tests, and units in variable names (`q_rad`, `p_m`).

Sources: https://docs.python.org/3/library/venv.html (only `python3 -m venv .venv` and the `.venv` convention), https://numpy.org/doc/stable/user/basics.broadcasting.html (only broadcasting).

## Ship It

`outputs/skill-numpy-robot-guards.md` reviews a robot script for missing shape and unit guards.

## Exercises

1. Add a `check_finite` guard that rejects NaN and infinity in a trajectory.
2. Make `looks_like_degrees` take a per-joint limit vector.
3. Show that `points @ R` rotates by `-theta`, using a test.
