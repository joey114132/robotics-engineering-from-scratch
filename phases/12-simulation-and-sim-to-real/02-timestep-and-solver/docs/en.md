# Timestep and Solver

> The step size and the integrator are part of the model, and a result that changes with them is not a result yet.

**Type:** Build   **Prerequisites:** 12/01 What a Simulator Approximates   **Time:** ~15 minutes

## In Plain Words

A crate drops onto a stiff spring pad. The squashed pad pushes it up, so it should rise to its drop height and no higher. A computer predicts this in fixed time steps. If a step moves the crate with its old speed, as if the pad's push had not started, the crate ends too deep in the pad and the pad stores extra energy.

The update rule is the integrator. Updating the speed first removes most of that energy, but too large a step can still fool you.

## The Problem

A robot link bounces higher off a stiff contact than it fell, or the arm jitters when you raise the time step. Only the numerical method changed, not the physics. Without varying the step you cannot tell a real effect from a calculation error.

## The Concept

![Two update orders](../assets/diagram-update-order.png)

*Explicit Euler moves `x` with the old velocity. Semi-implicit Euler updates velocity first and moves `x` with the new one.*

Take a mass on a spring (a linear oscillator) with position `x`, speed `v` and frequency `w`, updated every `dt` seconds. Explicit Euler multiplies its energy by `1 + (w*dt)^2` every step, so the energy always grows (drift). Semi-implicit Euler stays bounded: it exactly conserves a nearby shadow energy `v^2/2 + w^2 x^2/2 - dt*w^2*x*v/2`, so the true energy only wobbles. It is stable (never blows up) while `w*dt < 2`.

![Step-size sweep](../assets/diagram-dt-sweep.png)

*Take a tiny step as the reference, then raise `dt` until the result moves.*

![Drift and rebound](../assets/fig-dt-sweep.png)

*Left: at `dt` = 0.01 s explicit Euler drifts 39% in 10 s and semi-implicit 0.95%. Right: a 1 kg mass dropped 0.1 m onto a 10 kN/m contact. Explicit Euler rebounds to 0.14 m at 1 ms, semi-implicit stays within 5% up to 3 ms and returns 0.65 m at 19 ms.*

For small swings `w` = 2 rad/s, so `dt` = 0.01 s multiplies the energy by 1.0004 a step, 1.49 over 1000 steps (39% at the slower 1 rad swing). A correct bounce returns to 0.1 m. Explicit Euler returns 0.274 m at `dt` = 3 ms (2.7 times too high), 0.140 m at 1 ms and 0.103 m at 0.1 ms. Shrink `dt` until the answer stops moving.

![Three crates](../assets/clip-example.mp4)

*Explicit Euler at 3 ms, 1 ms, 0.1 ms, left to right, frozen at the first bounce's top. Only green reaches the amber drop-height ticks.*

## Build It

One step function covers both methods. The contact is a penalty spring that pushes up only below the floor.

```python
def step(method, x, v, acc, dt):
    if method == "euler":
        return x + dt * v, v + dt * acc(x)
    v = v + dt * acc(x)
    return x + dt * v, v
```

`pendulum_drift()` returns the worst energy error of an undamped pendulum over 10 s, and `rebound_height()` the apex after the first bounce, which should equal the drop height.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/12-simulation-and-sim-to-real/02-timestep-and-solver -q
python3 phases/12-simulation-and-sim-to-real/02-timestep-and-solver/code/main.py
```

## Use It

MuJoCo exposes `timestep` and `integrator` in the `option` element. Its default integrator is semi-implicit Euler, and it also offers RK4 and implicit variants. Rerun a contact task at half the step and compare.

Sources: MuJoCo XML reference, `option/timestep` and `option/integrator` (https://mujoco.readthedocs.io/en/stable/XMLreference.html, opened 2026-11-09).

## Ship It

`outputs/skill-timestep-sweep.md` is a checklist for proving a result does not depend on `dt`.

## Exercises

1. Halve the contact stiffness and check that the largest safe semi-implicit `dt` grows by about 1.4.
2. Find the largest `dt` at which the pendulum drift stays under 1%.
3. Explain why the 19 ms run is not a clean blow-up.
