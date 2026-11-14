# System Identification

> Fit the plant from a recording, and know that the recording decides which parameters you can learn.

**Type:** Build   **Prerequisites:** 12/01 What a Simulator Approximates   **Time:** ~15 minutes

## In Plain Words

Turn a hanging arm at one slow, steady speed and feel how hard you must push. Part of the push fights a constant rub and part fights a drag that grows with speed. At one speed the two parts add up to one number, so many different splits feel the same.

Now speed the arm up, slow it down and reverse it. The drag follows the speed and the rub does not, so the two can be told apart. System identification fits a model to such a recording.

## The Problem

You copy inertia `J` (how hard it is to speed up) from CAD, guess friction and drag, and tune by eye until one trajectory matches. The next trajectory misses because that single run could not tell the rub from the drag. The fit looked good; the parameters were wrong.

## The Concept

![Recording to parameters](../assets/diagram-id-pipeline.png)

*Short windows turn noisy speed samples into a linear problem for `J`, `b` and `c`. Motor lag `Tm` changes that problem, so a grid search over `Tm` repeats the solve.*

In one short window, the motor torque minus gravity, drag (`b` times speed) and rub (`c`, always against the motion), summed over the window, equals `J` times the speed change. Each sum comes from the recording, so `1/J`, `b/J` and `c/J` are the only unknowns, and least squares (smallest squared mismatch) finds them.

![Why a slow run cannot split b from c](../assets/diagram-collinear.png)

*At constant speed the drag term and the rub term are both constant, so least squares can only see their sum.*

![Fit, slow-run failure, excitation](../assets/fig-id-fit.png)

*Left: the model matches the data of a rich run (speed varies a lot). Middle: one slow constant-speed run returns `b` at -17 times its true value. Right: error against excitation size (how varied the motion is) with noise fixed. `J` falls below 0.1% and `c` to about 2%, while `b` stays near 8%.*

The slow run holds 0.28 rad/s, where drag `b = 0.02` pushes `0.02 * 0.28 = 0.0056` and rub `c = 0.05` pushes 0.05, in all 0.0556. The fit returned `b = -0.345` and `c = 0.153`, which total `-0.345 * 0.28 + 0.153 = 0.056`, so the data cannot choose between the two splits. In the rich run the speed reaches 3.35 rad/s, where `b = 0.02` pushes 0.067 but `b = 0` pushes nothing, so the fit returns `b = 0.0206`.

![Two recordings](../assets/clip-example.mp4)

*Watch both arms: one joint recorded at a steady speed (blue) and a varied speed (green).*

## Build It

Each candidate `Tm` filters the recorded command, builds the three sums and solves least squares. The lowest residual wins.

```python
for Tm in grid:
    X, y = design(d, Tm)
    th = np.linalg.lstsq(X, y, rcond=None)[0]
    fits.append((float(np.sum((y - X @ th) ** 2)), Tm, th, np.linalg.cond(X / np.linalg.norm(X, axis=0))))
```

Without noise the column-normalised condition number (how blurred the parameters are) is about 4 for the rich run, about 2400 for the slow one. `b` keeps a bias of about 8% from the window integrals.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/12-simulation-and-sim-to-real/03-system-identification -q
python3 phases/12-simulation-and-sim-to-real/03-system-identification/code/main.py
```

## Use It

`scipy.optimize.least_squares(fun, x0, bounds=...)` fits all four parameters at once and accepts bounds. Compare its answer with the grid fit.

Sources: signature and docstring checked in the local SciPy 1.11.4 (opened 2026-11-09).

## Ship It

`outputs/skill-excitation-check.md` checks a recording before you fit it.

## Exercises

1. Raise the noise until `J` is off by 20% and note which window length helps.
2. Add the known gravity `k` as a fourth unknown and check its condition number.
3. Design the smallest trajectory that still separates `b` from `c`.
