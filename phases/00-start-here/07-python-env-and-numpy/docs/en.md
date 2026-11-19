# Python Env and numpy

> See how a wrong unit or array shape quietly gives a wrong answer, and how to catch it.

**Type:** Build   **Prerequisites:** 00/06 Time Steps   **Time:** ~15 minutes

## In Plain Words

An arm's sensor reports the elbow angle as ninety. In degrees that is a quarter turn; in radians it is over fourteen turns. numpy, a Python add-on for grids of numbers, reads sin and cos angles as radians and never asks. So a wrong unit or array shape still runs. Only a check on the numbers as they arrive catches it.

## Key Terms

- **Radian**: a unit of angle where one full turn is about 6.28. Degrees use 360 for a full turn.
- **Array shape**: how many rows and columns an array has, such as 5 rows by 3 columns.
- **Rotation matrix**: a small grid of numbers that turns a point around an axis.
- **Transpose (`.T`)**: swaps the rows and columns of a matrix.
- **Guard**: a check on numbers as they arrive that stops bad ones with a clear error.
- **venv**: a private folder holding the Python add-ons for one project.

## The Problem

A robot arm's sensor says the elbow is at 90 degrees, and your code treats that number as radians. The hand ends up in the wrong place, and the program shows no error.

## The Concept

A robot does whatever its numbers say, so a wrong unit sends a real arm astray. numpy never checks units, so your code must.

![Degrees bug](../assets/diagram-degrees-bug.png)

*The sensor says 90 degrees, but the code reads 90 radians.*

Arrays have the same trap. Each point is a row, so to turn them all we first transpose the rotation matrix (swap its rows and columns). Skip that and the points turn the other way, with no error.

![Points are rows](../assets/diagram-shape-flow.png)

*Skipping the transpose turns the points the wrong way, silently.*

[![Two arms turn](../assets/clip-example.jpg)](../assets/clip-example.mp4)

*Green reaches the post. Blue skipped the transpose and swings away.*

![Wrong unit](../assets/fig-degrees-vs-radians.png)

*The wrong unit throws the hand far off.*

<details><summary>The math (optional)</summary>

`np.cos(90)` reads radians: 90 minus fourteen full turns is 2.04 radians (about 117 degrees), and its cosine is -0.448 instead of 0, so the horizontal coordinate is off by 0.45 of a link length. On a 0.4 m link that puts the tip 0.18 m from the right spot. Turning a point `p` is `R @ p`; points stored as rows need `points @ R.T`. Turning `(1, 0, 0)` by +90 degrees about z should give `(0, 1, 0)`, and `points @ R` gives `(0, -1, 0)`. Across sensor readings from 0 to 90, the horizontal error peaks at almost 0.8 m, as the last figure's right panel shows.

</details>

## Build It

One function checks an array's shape. Another flags values above one full turn in radians, which look like degrees.

```python
def check_shape(x, shape, name="array"):
    a = np.asarray(x, dtype=float)
    if a.ndim != len(shape) or any(s is not None and s != n for s, n in zip(shape, a.shape)):
        raise ValueError(f"{name}: expected shape {shape}, got {a.shape}")
    return a

def looks_like_degrees(q, limit=2 * np.pi):
    return bool(np.max(np.abs(q)) > limit)
```

`joint_angles` uses both; `rotate_z` only the shape check.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-start-here/07-python-env-and-numpy -q
python3 phases/00-start-here/07-python-env-and-numpy/code/main.py
```

## Use It

`python3 -m venv .venv` makes a private folder holding the Python add-ons for one project. Good habits: one venv per project, and a unit in every variable name, such as `angle_rad`.

Sources: https://docs.python.org/3/library/venv.html (venv only), https://numpy.org/doc/stable/user/basics.broadcasting.html (broadcasting only).

## Ship It

`outputs/skill-numpy-robot-guards.md` reviews a robot script for missing shape and unit guards.

## Exercises

1. Pass angles in degrees to `joint_angles` and read the error message.
2. Reject NaN.
3. Make `points` a 3-row array and `R` a rotation matrix from this lesson, then run `points @ R` and see which way it turns.
