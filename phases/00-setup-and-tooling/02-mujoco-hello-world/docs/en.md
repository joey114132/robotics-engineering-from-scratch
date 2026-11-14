# MuJoCo Hello World

> A simulator is a loop that turns forces into a new state every `dt`, so write one before you trust one.

**Type:** Build   **Prerequisites:** 00/01 Python Env and numpy   **Time:** ~15 minutes

## In Plain Words

Hang a ball on a rod like a playground swing and let go from the side. Without friction it never swings higher than where you let go.

A simulation moves the ball in small time steps of `dt` seconds. Each step changes the speed, then moves the ball. If the move uses the speed from before the change, the ball lags a step behind the force and each step adds a little energy. Using the new speed removes the lag.

## The Problem

You copy a physics loop from a forum and run a pendulum, a weight swinging on a rod. It swings a little higher every cycle until it spins. Nothing crashed and the equations look right. Only the order of two lines in the time step is wrong.

## The Concept

Read the boxes in order. An engine repeats them every time step `dt`.

![One physics step](../assets/diagram-physics-step.png)

*Acceleration changes velocity, and the new velocity moves the position. Using the old velocity instead is explicit Euler.*

Semi-implicit Euler is the loop in the diagram: new speed first, then move with it. Explicit Euler moves with the old speed. The pendulum is the smallest test. `theta` is its angle in radians from hanging down, `omega` its angular speed, `L` the rod length, `g` gravity (9.81). Gravity gives `omega' = -(g/L) sin(theta)`: the rate of change of `omega` follows the sideways pull `sin(theta)`. A small swing's period, one full swing and back, is `2 pi sqrt(L/g)`.

An explicit step multiplies a small swing's energy by about `1 + (g/L) dt^2`, slightly above one (1.016 at `dt` = 0.04 s with `L` = 1 m). Repeated, that lifts each swing higher. Release the ball at 0.5 rad for 10 s. Semi-implicit Euler stays at 0.50 rad. Explicit Euler climbs to 2.46 rad, almost five times higher. At `dt` = 0.01 s it still reaches 0.78 rad.

![Three pendulums](../assets/clip-example.mp4)

*Three pendulums at 1.8 times real speed. Watch the amber line, the release height. Blue (explicit Euler, `dt` 0.04 s) climbs far above it, pale blue (explicit Euler, `dt` 0.01 s) climbs slowly, green (semi-implicit Euler) stays on it.*

We also solve one pendulum with two solvers, our loop and MuJoCo, a physics engine.

![Same pendulum, two solvers](../assets/diagram-two-solvers.png)

*Our loop and MuJoCo give the same period.*

![Step-size error](../assets/fig-step-size.png)

*Left: watch explicit Euler's energy climb. Right: halving `dt` cuts the period error, against the exact period, to about a quarter.*

## Build It

One step, then a loop. The only difference between the two schemes is which `omega` moves the angle.

```python
def step(theta, omega, dt, L=1.0, scheme="semi"):
    omega_new = omega - dt * (G / L) * np.sin(theta)
    return theta + dt * (omega_new if scheme == "semi" else omega), omega_new

def simulate(theta0, dt, seconds, L=1.0, scheme="semi"):
    theta, omega, out = theta0, 0.0, [theta0]
    for _ in range(int(round(seconds / dt))):
        theta, omega = step(theta, omega, dt, L, scheme)
        out.append(theta)
    return np.array(out)
```

`measure_period` finds upward zero crossings of the angle and interpolates inside the step. The time between two is one period.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-setup-and-tooling/02-mujoco-hello-world -q
python3 phases/00-setup-and-tooling/02-mujoco-hello-world/code/main.py
```

## Use It

`mujoco_period()` builds the same pendulum from an inline MJCF string (MuJoCo's XML model format) and calls `mujoco.mj_step`. Its period agrees with ours to within 0.5% (tested, skipped if MuJoCo is missing). The MuJoCo XML reference lists `integrator` with default `Euler`, described as semi-implicit Euler; the docs also recommend `implicitfast`.

Sources: https://mujoco.readthedocs.io/en/stable/XMLreference.html

## Ship It

`outputs/skill-sim-sanity-check.md` is a checklist for trusting a new simulation: period, energy and step size.

## Exercises

1. Add damping to `step` and check that the energy now falls.
2. Find the largest `dt` at which the period error stays under 1%.
3. Change `L` in the MJCF string and confirm the period scales with `sqrt(L)`.
