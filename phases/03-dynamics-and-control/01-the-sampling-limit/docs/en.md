# The Sampling Limit

> Learn why a brake that works on paper can make a robot joint buzz, and how to tell in advance.

**Type:** Build   **Prerequisites:** none   **Time:** ~15 minutes

## In Plain Words

Picture a bench arm swinging at the elbow, with a motor that brakes the swing. The controller reads the speed once, then pushes against it with a steady force until its next reading.

A gentle push slows the arm. A strong push, a light arm or a long wait lets the push outlast the stop and shove the arm back, faster than before.

## Key Terms

- **Damper**: a brake that pushes against speed with a torque proportional to it.
- **Damping gain (`kd`)**: how strongly the damper brakes.
- **Tick (`dt`)**: one control step, the time between two controller readings.
- **Inertia (`J`)**: how hard a joint is to speed up or slow down.
- **Host**: the computer that runs the controller loop.
- **Torque**: the twisting force a motor applies to a joint.

## The Problem

A robot joint shakes, so you turn up the brake (damping gain `kd`), and now it buzzes. The host computes a torque once per tick and holds it, so the damper pushes against a speed one tick old.

## The Concept

A controller acts in steps, and that delay can turn a brake into a shove.

![Stale velocity](../assets/diagram-stale-command.png)

*The torque uses the speed at tick start but acts all tick.*

Take a pure inertia `J`. Hold the torque `-kd * v` for one tick `dt`: the speed changes by `-dt * kd * v / J`, so one tick later `v+ = v * (1 - r)`, where `r = dt * kd / J`.

![Three zones of r](../assets/diagram-r-zones.png)

*Up to 1 the speed shrinks smoothly (at 1, to zero in one tick). Between 1 and 2 it flips sign but shrinks. Above 2 it grows.*

![Speed per tick](../assets/fig-r-response.png)

*Left: `r = 1.5` flips the sign but the swings shrink. Right: `1 - r` crosses 0 at `r = 1`.*

Example: `J = 0.02`, `dt = 0.001`, `kd = 30` gives `r = 1.5`: speeds 1, -0.5, 0.25. Tripling `J` gives `r = 0.5`: 1, 0.5, 0.25.

![Two arms](../assets/clip-example.mp4)

*Same `kd = 30`. Light blue (`r = 1.5`) jerks in shrinking steps; weighted green (`r = 0.5`) glides to a stop.*

## Build It

```python
def step_damper(v, J, kd, dt):
    return v * (1.0 - dt * kd / J)

def classify(J, kd, dt):
    r = dt * kd / J
    return "smooth" if r <= 1 else "chatter" if r < 2 else "divergent"
```

Tests cover both sides of each boundary at `J = 0.02`, `dt = 0.001` (limits `kd = 20` and `40`), and check that `r = 1` gives zero speed.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/01-the-sampling-limit -q
python3 phases/03-dynamics-and-control/01-the-sampling-limit/code/figure.py
```

## Use It

Many drives run an inner loop much faster, which removes the limit. Otherwise lower `kd`, raise the loop rate, or cap gains using the lowest-inertia pose.

## Ship It

`outputs/skill-sampling-limit-check.md` computes `r` for every damped joint in a gain file.

## Exercises

1. Add a spring term and find the stable `(kp, kd)` region by simulation.
2. Add one tick of delay; where do the limits move?
3. Estimate a two-link wrist's effective inertia.
