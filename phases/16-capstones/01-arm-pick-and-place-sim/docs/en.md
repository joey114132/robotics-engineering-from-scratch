# Arm Pick and Place in Simulation

> Four earlier ideas make one task, and removing the quietest one, gravity feedforward, makes the whole task fail.

**Type:** Build   **Prerequisites:** 02/02 Inverse Kinematics, 03/02 Gravity Compensation, 09/01 Trajectory Profiles   **Time:** ~30 minutes

## In Plain Words

A bench arm lifts a ball off a post (A) and sets it on a marker (B). Gravity pulls the whole arm down, so the arm needs a steady upward push just to hold still.

Gravity feedforward adds that push in advance. Without it, the controller pushes back only after the arm has sagged, and the push grows with the sag. The arm therefore settles lower than planned, and the ball lands beside the marker.

## The Problem

Every earlier lesson passes its own test, yet in this run the ball lands 2 cm from the marker. Here you build the whole chain in simulation and learn where a miss comes from.

## The Concept

![Parts of the pick-and-place system](../assets/diagram-pick-place-system.png)

*Follow the numbers. IK (inverse kinematics) finds the joint angles that put the hand on each stop, a quintic (a curve that starts and ends at rest) joins them, and a PD loop (push for error, brake for speed) drives the arm along it with gravity feedforward added.*

![Break test diagram](../assets/diagram-pick-place-broken.png)

*Read the chain from the left: without feedforward all of gravity's torque becomes error, which the position spring turns into sag.*

Hold the arm at B. The shoulder must carry 6.11 Nm (`gravity()`). With `kp = 150` (Nm of push per radian of error) and no feedforward the spring must supply all of it, so the shoulder sinks about `6.11 / 150 = 0.04` rad. The tip is about 0.5 m from the shoulder, so it moves about `0.04 × 0.5 = 0.02` m. `run()` reports 20.24 mm.

![Two bench arms hold a ball over the marker while one loses its feedforward](../assets/clip-example.mp4)

*Watch the blue arm when its feedforward is switched off: it sinks about 0.04 rad and stops 20 mm from the marker. The green arm keeps it and stays put. Sag is drawn 6 times larger.*

![The task succeeding](../assets/fig-pick-place-result.png)

*Watch the tip: hover over A, pick, lift, hover over B, place. It lags the plan by up to 9 mm while moving, because the controller reacts only after an error appears, then settles to 0.00 mm at B.*

![Sag against the plan](../assets/fig-pick-place-sag.png)

*Compare with the last picture: without feedforward the tip sits 14 to 37 mm off the plan and places 20 mm from B, so the check fails.*

## Build It

The new part is the arm itself: `M(q) a + C(q, v) + g(q) = tau` (inertia, motion-coupling and gravity terms), stepped every millisecond.

```python
q, v = step(q, v, ff * gravity(qd) + kp * (qd - q) + kd * (vd - v))
```

`ik()` gives the waypoints, `reference()` gives the planned angles and speeds `qd, vd` along quintic segments, and `ff` scales the feedforward from `gravity()`. `run()` returns the pick error, the place error and `passed` (place error below 5 mm). A free-swing energy test checks the Coriolis terms.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/16-capstones/01-arm-pick-and-place-sim -q
python3 phases/16-capstones/01-arm-pick-and-place-sim/code/main.py
```

## Use It

Real simulators supply `M`, `C` and `g` for you. MuJoCo's `qfrc_bias` is documented as `C(qpos,qvel)`, computed by `mj_fwdVelocity`. Compare it with `coriolis + gravity` from this lesson.

Sources: [MuJoCo mjData reference](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html), read 2026-11-09.

## Ship It

`outputs/skill-pick-place-miss-triage.md` turns a miss at B into the likely stage that caused it.

## Exercises

1. Scale the feedforward to 0.9 and find the smallest `kp` that still passes.
2. Add a 0.5 kg block to link 2 after the pick and watch the place error.
3. Replace the quintic path with a trapezoid and compare the peak tracking error.
