# Model Predictive Control

> Learn how a controller can plan ahead while respecting a motor's limits.

**Type:** Build   **Prerequisites:** 03/06 LQR   **Time:** ~15 minutes

## In Plain Words

Imagine steering a toy car to a stop line with a weak brake. If you brake only at the line, you shoot past it, so you must start early.

Model predictive control plans the next few pushes with that brake limit built in. It applies only the first push, measures the car again, then plans again.

## Key Terms

- **Model predictive control (MPC)**: plan a short future under the limits, apply the first command, then plan again.
- **Horizon (`N`)**: how many steps ahead each plan looks.
- **Cost**: a score for how bad a plan is.
- **Terminal cost**: a price on where the plan ends, so a short plan still sees what comes after.
- **Quadratic**: a cost shaped like a bowl, easy to minimise.
- **Box constraint**: every push must stay within plus or minus the biggest allowed push.

## The Problem

A robot's motor can only push so hard. A controller (the program steering the arm) asks for more, the command is clipped, and since it never knew the limit it brakes too late and overshoots.

## The Concept

Real motors have limits, so plan with them instead of asking for the impossible and clipping. Model predictive control plans the next few pushes with the limit built in, applies only the first, measures again, and plans again.

![The receding-horizon loop](../assets/diagram-mpc-loop.png)

*Every step the plan is rebuilt from what was measured.*

![Clip or plan](../assets/diagram-mpc-clip.png)

*Two places for the limit: clipped after the controller, or built into the plan (MPC).*

![Clipped LQR vs MPC](../assets/fig-mpc-vs-clip.png)

*With a weak brake, the clipped controller overshoots far more.*

Looking further ahead helps.

![Three plan lengths](../assets/clip-example.mp4)

*Plans of 2, 10 and 20 steps; amber bars show the slide past the line.*

<details><summary>The math (optional)</summary>

Stack the next `N` states as `X = Phi x0 + Gam U`. The cost plus a terminal cost is a bowl in `U`, and `|u| <= umax` is a box. Solve by downhill steps clipped into the box (Nesterov momentum). Start 4 m away with `umax = 0.5`: the clipped gain overshoots by 1.28 m; `N = 20` (2 s ahead at `dt = 0.1`) by 0.31 m. `N = 2` (0.2 s ahead) overshoots by 1.27 m, `N = 10` by 0.78 m.

</details>

## Build It

Two short lines solve the planning problem (details in the fold).

```python
U_new = np.clip(Y - step * (H @ Y + f), -umax, umax)   # projected gradient
Y = U_new + (t - 1) / t_new * (U_new - U)               # momentum
```

`prediction()` works out where the car ends up for a list of pushes, `plan()` finds the lowest-cost list that stays within the limit, and `simulate()` plans again every step. Tests check the prediction against a real run, that the limit is obeyed, and that a loose limit matches LQR.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/08-model-predictive-control -q
python3 phases/03-dynamics-and-control/08-model-predictive-control/code/figure.py
```

## Use It

Real systems use a ready-made solver library such as OSQP; solve one step with it and compare the first push with `plan()`.

Sources: [OSQP documentation](https://osqp.org/docs/), checked 2026-11-10.

## Ship It

`outputs/skill-mpc-setup-check.md` reviews horizon, weights, terminal cost and solve time.

## Exercises

1. Change the plan length and watch the overshoot.
2. Add a speed limit. Which numbers must the plan now keep inside limits?
3. Stop `plan()` after 20 loops (set `iters=20`) and see how much the cost rises.
