# Numerical Inverse Kinematics

> Learn how to find joint angles by trial and correction when no formula exists.

**Type:** Build   **Prerequisites:** 02/03 Jacobian and Velocity, 02/04 Singularities   **Time:** ~15 minutes

## In Plain Words

A three-link bench arm must touch a ball, and no formula gives the joint angles. Bend the joints a little, see where the hand went, and correct. A big bend can overshoot; a joint at its stop cannot bend further.

Numerical inverse kinematics repeats these small corrections, using the Jacobian to predict each one. The starting pose decides which answer it finds, so it restarts from several.

## Key Terms

- **Numerical IK**: finding joint angles by repeated small corrections instead of a formula.
- **Seed**: the starting pose of one run.
- **Joint limit**: how far a joint may turn; the joint stops there.
- **Clamp**: cut a value back to the allowed range.
- **Converged**: the error has fallen below the tolerance, here 1e-6 m.
- **Jacobian**: the matrix that predicts how the tip moves for a small joint change.

## The Problem

You want a robot arm's hand at a point, but a six-joint arm has no formula for the angles. They must respect the joint limits and not depend on the start.

## The Concept

Most real arms have no angle formula, so robots find angles by trying and correcting.

`e` is the tip error: the target minus where the tip is now.

![One step of the iteration](../assets/diagram-ik-loop.png)

*Measure the error, solve a small joint step, clamp it, run FK, repeat.*

The step is the damped solve from 02/04, `dq = J^T (J J^T + lam^2 I)^-1 e`. Damping keeps it finite at a straight arm.

The Jacobian predicts only small moves, so a cap on the biggest joint step prevents overshoot. The solver has converged when the error falls below 1e-6 m.

![Restarts](../assets/diagram-ik-restarts.png)

*Each seed slides into a nearby solution; both elbow bends show up.*

![Ghost arms and convergence](../assets/fig-numerical-ik.png)

*Left: eight seeds, one target. Right: reachable targets fall below 1e-6 m within about 16 steps; an unreachable one stays flat.*

For links of 0.4, 0.3 and 0.2 m and target (0.5, 0.3) m, 17 of 20 seeds converge. Seed 0 takes 6 steps, elbow up; seed 2 takes 7, elbow down.

![Two start poses reach the same ball](../assets/clip-example.mp4)

*Each arm runs `solve_ik()` one step at a time from its own seed.*

## Build It

```python
J = jacobian(q, L)
dq = J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(2), e)
q = np.clip(q + dq * min(1.0, max_step / np.abs(dq).max()), lo, hi)
```

`solve_ik()` returns `(q, converged)`; for an unreachable target it returns the closest pose and `False` instead of raising. `ik_restarts()` runs it from random seeds so you can pick the solution nearest the current pose.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/05-numerical-inverse-kinematics -q
python3 phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/code/main.py
```

## Use It

Compare with `scipy.optimize.least_squares` on `fk(q) - target` with `bounds=(lo, hi)`. Craig, chapter 4, covers the closed form.

## Ship It

`outputs/skill-ik-solver-check.md` reviews an IK solver for limits, restarts and failure flags.

## Exercises

1. Pick the restart solution closest to the current `q`.
2. Add a fourth link and count how many restarts converge.
3. Set `lam = 0` and start from the straight arm.
