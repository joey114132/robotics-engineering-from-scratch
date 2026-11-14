# Numerical Inverse Kinematics

> With no formula, nudge the joints toward the target with the Jacobian, clamp to limits, and restart from several poses.

**Type:** Build   **Prerequisites:** 02/03 Jacobian and Velocity, 02/04 Singularities   **Time:** ~15 minutes

## In Plain Words

A three-link bench arm must touch a ball, and no formula gives the joint angles. So bend the joints a little, see where the hand went, and correct. A big bend can overshoot, and a joint at its stop cannot bend further. Out of reach, the arm ends stretched toward it.

Numerical inverse kinematics repeats these small corrections, using the Jacobian to predict each one. The starting pose decides which answer it finds, so it restarts from several. It reports whether the hand reached the ball.

## The Problem

Lesson 02/02 solved a two-link arm with the law of cosines. Now you have a three-link arm that can reach a point in many ways, or a six-joint arm with no neat formula. You need joint angles for a target, they must respect the joint limits (how far each joint may turn), and the answer should not depend on where you started.

## The Concept

The first picture is one correction step, and the loop repeats it. `e` is the tip error: the target minus where the tip is now.

![One step of the iteration](../assets/diagram-ik-loop.png)

*Measure the error, solve for a small joint step, clamp it, run forward kinematics, and repeat until the error is tiny.*

The step is the damped solve from 02/04: `dq = J^T (J J^T + lam^2 I)^-1 e`. The damping keeps the step finite at a straight arm, where the plain inverse does not exist.

The Jacobian predicts only small moves, so a big step lands where the prediction is wrong. A cap on the biggest joint step prevents that. The solver has converged when the error falls below 1e-6 m.

A seed is a starting pose. Next: many seeds.

![Restarts](../assets/diagram-ik-restarts.png)

*Each random seed slides into a nearby solution. Both elbow bends show up, and a seed pushed against a limit reports that it failed.*

![Ghost arms and convergence](../assets/fig-numerical-ik.png)

*Left: eight seeds, one target, different arm shapes. Right: reachable targets drop below 1e-6 m within about 16 steps; an unreachable one stays flat.*

Take the target (0.5, 0.3) m for the arm with links of 0.4, 0.3 and 0.2 m. In `ik_restarts()`, 17 of 20 random seeds converge (tip within 1e-6 m). Seed 0 gets there in 6 steps with the elbow up. Seed 2 needs 7 steps and ends elbow down. Watch both hands settle on the same ball with different arm shapes.

![Two start poses reach the same ball](../assets/clip-example.mp4)

*Each arm runs `solve_ik()` one step at a time from its own seed.*

## Build It

```python
J = jacobian(q, L)
dq = J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(2), e)
q = np.clip(q + dq * min(1.0, max_step / np.abs(dq).max()), lo, hi)
```

`solve_ik()` returns `(q, converged)`. It never raises for a target it cannot reach. It hands back the closest pose it found and `False`. `ik_restarts()` runs it from random seeds inside the limits, so you can pick the solution nearest the current pose.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/05-numerical-inverse-kinematics -q
python3 phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/code/main.py
```

## Use It

Compare with `scipy.optimize.least_squares` on `fk(q) - target` with `bounds=(lo, hi)`. Both should land on poses whose `fk` matches. Craig, chapter 4, covers the closed-form case that this replaces.

## Ship It

`outputs/skill-ik-solver-check.md` reviews an IK solver for limits, restarts and failure flags.

## Exercises

1. Pick the restart solution closest to a given current `q` and compare it with the first converged one.
2. Add a fourth link and count how many restarts converge.
3. Set `lam = 0` and start from the straight arm to see what happens.
