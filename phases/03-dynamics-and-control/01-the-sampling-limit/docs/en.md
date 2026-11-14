# The Sampling Limit

> A damper (a brake on speed) that is correct in continuous time can still be unstable once the controller holds its command for one tick.

**Type:** Build   **Prerequisites:** none   **Time:** ~15 minutes

## In Plain Words

Picture a bench arm swinging at the elbow, with a motor that brakes the swing. The controller looks at the swing speed once, then pushes against that speed with a steady force until its next look.

A gentle push slows the arm. If the push is strong, the arm is light or the wait is long, the push lasts past the moment the arm stops and shoves it back the other way. A strong enough shove sends it back faster than before, so each swing grows.

## The Problem

You raise a damping gain `kd` (braking strength) so a joint stops oscillating, and it starts buzzing instead. The gain looked mild. The host (the controller's computer) computes a torque once per tick, one control step, and holds it, so the damper pushes against a speed that is already one tick old.

## The Concept

![Stale velocity](../assets/diagram-stale-command.png)

*The torque comes from the speed at tick start but acts all tick, so by the red box it is out of date.*

Take a pure inertia `J` (how hard the joint is to speed up or slow down). Hold the torque `-kd * v` for the tick length `dt`. Torque is inertia times acceleration, so the speed changes by `-dt * kd * v / J`. One tick later it is `v+ = v * (1 - r)`, where `r = dt * kd / J`.

![Three zones of r](../assets/diagram-r-zones.png)

*Up to 1 the speed shrinks smoothly (at exactly 1, to zero in one tick). Between 1 and 2 it flips sign but still shrinks. At exactly 2 it keeps its size, and above 2 it grows.*

![Speed per tick](../assets/fig-r-response.png)

*Watch `r = 1.5` on the left: the sign flips, the swings shrink. Right: `1 - r` crosses 0 at `r = 1` and -1 at `r = 2`.*

`J` is in the ratio, so the lightest joint crosses the `r = 1` line first at a gain that feels mild on the shoulder.

Example: `J = 0.02`, `dt = 0.001`, `kd = 30` gives `r = 1.5`, so each tick multiplies the speed by `-0.5` (1, -0.5, 0.25). A weight that triples `J` gives `r = 0.5` (1, 0.5, 0.25).

![Two arms](../assets/clip-example.mp4)

*Same `kd = 30`. Watch the blue arm: light (`r = 1.5`), it jerks back and forth in shrinking steps. The green arm carries a weight (`r = 0.5`) and glides to a stop. One tick is drawn a third of a second.*

## Build It

```python
def step_damper(v, J, kd, dt):
    return v * (1.0 - dt * kd / J)

def classify(J, kd, dt):
    r = dt * kd / J
    return "smooth" if r <= 1 else "chatter" if r < 2 else "divergent"
```

Tests cover both sides of each boundary at `J = 0.02`, `dt = 0.001` (limits `kd = 20` and `40`) and check that `r = 1` gives zero speed with no sign flip.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/01-the-sampling-limit -q
python3 phases/03-dynamics-and-control/01-the-sampling-limit/code/figure.py
```

## Use It

Many drives run an inner loop (inside the motor drive) at a much higher rate, which removes the limit from the host loop. When damping must stay on the host, lower `kd`, raise the loop rate, or gate gains with the inertia of the lowest-inertia pose.

## Ship It

`outputs/skill-sampling-limit-check.md` computes `r` for every damped joint in a gain file.

## Exercises

1. Add a spring term and find the stable region in the `(kp, kd)` plane by simulation.
2. Add one tick of delay to the held command. Where do the limits move?
3. Estimate the effective inertia of a two-link wrist from lesson 03/02.
