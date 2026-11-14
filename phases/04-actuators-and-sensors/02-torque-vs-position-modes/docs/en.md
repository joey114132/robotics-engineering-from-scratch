# Torque vs Position Modes

> A position mode is a torque mode with someone else's PD gains, and those gains set how stiff your joint feels.

**Type:** Build   **Prerequisites:** 04/01 Motor and Gearbox, 03/03 Impedance Control   **Time:** ~15 minutes

## In Plain Words

Press up on the hand of a bench arm. Inside the joint, the drive pulls the hand back toward its target angle like a spring, and the strength of that spring is fixed in the drive. Your program can ask for a softer spring, but in position mode the request never reaches it, so the arm barely gives way.

In torque mode your program writes the pull itself, so it decides how much pull each unit of error gets.

## The Problem

You write an impedance controller, one that lets a joint give way like a spring, with stiffness `K = 20` Nm per radian. On the drive you have, the joint stays stiff and barely moves when you push it. Your program asked for softness, but the drive's own position controller never heard it.

## The Concept

A PD controller pulls back with `kp` Nm per radian of error and brakes with `kd` in proportion to speed. In each row of the picture, look at who runs one: your program in torque mode, the drive in position mode.

![Who writes the torque](../assets/diagram-mode-loops.png)

*In torque mode your program writes the torque. In position mode the drive's inner PD, a spring with fixed gains, does.*

The drive's inner one has fixed `kp_in` and `kd_in`. A constant push `tau_ext` moves the joint until the spring balances it: `tau_ext / K` in torque mode, so `K` is yours to choose, but `tau_ext / kp_in` in position mode, whatever `K` you send.

With a 2 Nm push and `kp_in = 400`, torque mode with `K = 20` gives way `2 / 20 = 0.1` rad and position mode only `2 / 400 = 0.005` rad. An admittance layer wants the joint to act like a spring of stiffness `K`, so it measures the push and lifts the target by `tau_ext / K = 0.1` rad. With the inner spring's `0.005` the total is `tau_ext * (1/K + 1/kp_in) = 0.105` rad, never stiffer than `kp_in`.

Watch the green target rise.

![Position mode without and with an admittance layer](../assets/clip-example.mp4)

*Both in position mode. Blue: no layer, the hand barely moves. Green: the layer lifts the amber target and the hand follows.*

Follow the boxes from the wish for a soft joint.

![What the outer controller can ask for](../assets/diagram-mode-options.png)

*Impedance needs torque commands. A position-only drive needs an outside torque-measuring layer.*

![Response to a push and felt stiffness](../assets/fig-mode-stiffness.png)

*Left: the same 2 Nm push moves three joints by different amounts. Right: stiffness requested against stiffness felt, and only torque mode follows the dotted line.*

## Build It

One joint `J*qdd = tau - b*qd + tau_ext`, three ways to produce `tau`.

```python
if mode == "torque":
    tau = K * (q_des - q) - D * qd
elif mode == "position":
    tau = kp_in * (q_des - q) - kd_in * qd
elif mode == "admittance":
    tau = kp_in * (q_des + ext / K - q) - kd_in * qd
```

A test shows `position` equals `torque` with `K = kp_in, D = kd_in`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/02-torque-vs-position-modes -q
python3 phases/04-actuators-and-sensors/02-torque-vs-position-modes/code/figure.py
```

## Use It

ros2_control joints declare command interfaces (the commands a drive accepts), such as position or effort, and a controller fails if it asks for one the hardware lacks. Check your drive's first.

Sources: [ros2_control full tutorial](https://control.ros.org/master/doc/ros2_control_demos/example_7/doc/userdoc.html), accessed 2026-11-09.

## Ship It

`outputs/skill-drive-mode-check.md` decides whether a drive can host impedance control.

## Exercises

1. Raise `kp_in` to 4000 and measure how the admittance deflection changes.
2. Add a 3 ms delay to the measured push and watch the admittance loop.
3. Find the `K` at which the admittance layer feels half as stiff as requested.
