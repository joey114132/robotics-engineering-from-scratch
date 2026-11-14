# Quadrotor Model

> A quadrotor cannot push sideways. It tilts first, and the tilt turns thrust into sideways force.

**Type:** Build   **Prerequisites:** 10/01 Inverted Pendulum and ZMP   **Time:** ~15 minutes

## In Plain Words

A quadrotor model predicts a drone's motion from its tilt and its thrust, the upward push its propellers get by throwing air down. Hold a showerhead and the water pushes your hand the other way. Tilt the showerhead and the push tilts with it.

A hovering drone works the same way. Its propellers push air straight down, so the air pushes the drone straight up. Tilt the drone and part of that push shoves it sideways, so less holds it up. At the same thrust, a tilted drone sinks.

## The Problem

You command a drone to move 1 m to the right and at first it seems to ignore you. Then it tips, drifts and loses height. That comes from the vehicle having only two inputs, total thrust and one torque, and three things to move.

## The Concept

![One thrust, split by the tilt](../assets/diagram-thrust-split.png)

*The thrust always points along the body axis. Pitch `theta`, the tilt angle, decides how much goes up and how much sideways.*

Take the planar model with state `x, z, theta` (sideways position, height, tilt) and inputs `T` (total thrust) and `tau` (pitch torque, the twist that tilts the drone). `m` is mass, `g` gravity and `I` how hard the drone is to twist:

`m x'' = T sin(theta)`, `m z'' = T cos(theta) - m g`, `I theta'' = tau`.

At `theta = 0` and `T = m g` every acceleration is zero, so the hover thrust is `m g`. Tilt by `theta` and keep that thrust, and the height acceleration is `g (cos(theta) - 1)`, which is negative. Holding height needs `T = m g / cos(theta)`, which gives a sideways acceleration `g tan(theta)`.

Example: tilt a 0.5 kg drone by 20 degrees. At `T = m g = 4.9 N` the height acceleration is -0.59 m/s^2, so it sinks 0.30 m in 1 s. Holding height needs 5.2 N (6% more), and the sideways acceleration is 3.6 m/s^2.

![Two tilted drones, two thrusts](../assets/clip-example.mp4)

*Both drones are held at 20 degrees for 1 s. Watch the amber ball and line (start height): blue (`T = m g`) sinks below them, green (`T = m g / cos(theta)`) keeps its height. Drones drawn 1.6 times larger.*

![Torque to position](../assets/diagram-torque-to-position.png)

*Torque reaches position through four integrations (rate, angle, speed, position), so a steady torque gives `x = g tau t^4 / (24 I)` for small angles.*

![Thrust step versus torque step](../assets/fig-tilt-then-move.png)

*Left: 10% extra thrust only climbs. Right: a torque of 0.002 Nm tilts the body 1 degree at 0.27 s but moves it 1 cm only at 0.47 s.*

## Build It

```python
def deriv(s, T, tau, m, I, g=G):
    th = s[2]
    return np.array([s[3], s[4], s[5], T*np.sin(th)/m, T*np.cos(th)/m - g, tau/I])
```

State is `[x, z, theta, vx, vz, omega]`. `simulate()` steps the equations forward in time (RK4) with a control function. The example uses made-up values `m = 0.5 kg` and `I = 0.004 kg m^2`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/03-quadrotor-model -q
python3 phases/10-legged-and-aerial/03-quadrotor-model/code/main.py
```

## Use It

The last test compares the end state with SciPy's `solve_ivp`. A real vehicle maps `T` and `tau` to four motor speeds with a mixer, outside this lesson.

## Ship It

`outputs/skill-quadrotor-model-check.md` reviews a quadrotor model or controller for hover thrust, tilt coupling and units.

## Exercises

1. Tilt 30 degrees at `T = m g / cos(theta)` and find the sideways acceleration.
2. Find how long a 0.004 Nm torque takes to reach 10 degrees.
3. Add a drag force `-c vx` and find the new steady speed.
