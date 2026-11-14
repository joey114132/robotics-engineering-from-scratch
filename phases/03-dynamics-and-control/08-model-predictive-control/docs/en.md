# Model Predictive Control

> Plan a short future with the limits written in, apply only the first command, then plan again.

**Type:** Build   **Prerequisites:** 03/06 LQR   **Time:** ~15 minutes

## In Plain Words

Imagine steering a toy car to a stop line with a weak brake. If you wait until the line to brake, you shoot past it. You must start early, judging from the speed how far the car needs to stop.

Model predictive control plans the next few pushes with that brake limit built in. It applies only the first push, measures the car again, then plans again. Planning with the limit overshoots less than asking for a huge push and cutting it off.

## The Problem

A controller asks for more torque than the motor has, and the command is simply clipped. The controller never knew about the limit, so it brakes too late and overshoots. The error then keeps pushing the other way, and the arm swings back across the target.

## The Concept

![The receding-horizon loop](../assets/diagram-mpc-loop.png)

*Every tick the plan is rebuilt from the measured state. Only its first step ever reaches the plant, the thing being controlled.*

Stack the next `N` states (the horizon) as `X = Phi x0 + Gam U`, where `x0` is the measured state, `U` holds the next `N` pushes, and `Phi` and `Gam` come from lesson 06's model. The cost `sum x'Qx + u'Ru` plus a terminal cost (a price on where the plan ends) becomes a quadratic in `U`, a bowl that is easy to minimise. The limit `|u| <= umax` is a box on `U`: every push stays within the bounds. To solve it, take gradient steps (small downhill moves) and clip back into the box after each one, with Nesterov momentum to converge faster. Using LQR's `P` as the terminal cost lets a short plan still see the cost beyond its end.

![Clip or plan](../assets/diagram-mpc-clip.png)

*The difference is where the limit lives: after the controller, or inside it.*

![Clipped LQR vs MPC](../assets/fig-mpc-vs-clip.png)

*A double integrator starts 4 m away with `umax = 0.5`. The clipped gain overshoots by 1.28 m. MPC with `N = 20` (2 s ahead at `dt = 0.1`) overshoots by 0.31 m. Right: the plan at 4 s looks 2 s ahead and only its first step is used.*

Example: same start and `umax = 0.5`, only the plan length changes. With `N = 2` (0.2 s ahead) the car overshoots by 1.27 m, with `N = 10` by 0.78 m and with `N = 20` by 0.31 m.

![Three plan lengths](../assets/clip-example.mp4)

*Plans of 2, 10 and 20 steps (the green car looks 2 s ahead). Watch how far each car slides past the line. Played at 2x speed.*

## Build It

```python
U_new = np.clip(Y - step * (H @ Y + f), -umax, umax)   # projected gradient
Y = U_new + (t - 1) / t_new * (U_new - U)               # momentum
```

`prediction()` builds `Phi` and `Gam`. `plan()` solves the box-constrained problem. `simulate()` re-plans every tick. Tests check that the prediction reproduces a rollout, that applied inputs obey the bound, and that with a loose bound MPC matches LQR.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/08-model-predictive-control -q
python3 phases/03-dynamics-and-control/08-model-predictive-control/code/figure.py
```

## Use It

Production MPC uses a dedicated QP solver such as OSQP, with a warm start from the last plan. Solve one tick with it and compare the first input with `plan()`. The horizon trades cost against compute.

Sources: [OSQP documentation](https://osqp.org/docs/), checked 2026-11-10.

## Ship It

`outputs/skill-mpc-setup-check.md` reviews horizon, weights, terminal cost and solve time.

## Exercises

1. Add a bound on velocity as a second constraint and describe what the box becomes.
2. Find the smallest `N` whose cost is within 1% of `N = 30`.
3. Stop the solver after 20 iterations and measure how much the cost rises.
