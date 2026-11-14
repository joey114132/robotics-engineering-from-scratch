# Walking by Foot Placement

> A walker steers its speed with its feet: the next foot position is solved from where the body is now.

**Type:** Build   **Prerequisites:** 10/01 Inverted Pendulum and ZMP   **Time:** ~15 minutes

## In Plain Words

When you walk, you control your speed with where each foot lands. Land the foot well ahead and your body ends up behind it, so gravity pulls you back and you slow down. Land it too close and your body passes over the foot, so gravity pulls you forward and you speed up.

A walking model picks each spot from the body's position and speed, so the next step ends at the requested speed. Too-short steps raise the speed a little more each step.

## The Problem

You ask a walking model for 0.6 m/s with a fixed, plausible step length. At first it looks fine, then each step is faster than the last until the body is far ahead of its feet. The steps were a little short, so gravity kept pushing the body on instead of slowing it.

## The Concept

![One step of foot placement](../assets/diagram-foot-placement-loop.png)

*At the end of each stance (the time one foot stays down) the controller reads the body position `x` and speed `v` and picks the next foot.*

Stance lasts `T`, and the next foot sits at `p` (`Tc` and `h`: the fall's time scale and body height from lesson 01). Write `u = x - p` for how far the body is ahead of that foot at touchdown (when it lands). Lesson 01's `lipm_state` gives the speed at the end of the stance: `v' = (u/Tc) sinh(T/Tc) + v cosh(T/Tc)`, (`v'` is that speed; `sinh` and `cosh` mix `exp(t/Tc)` and `exp(-t/Tc)`). Setting `v' = v_target` (the requested speed) and solving for `u` gives the foot: `p = x - u`. This is one-step deadbeat: the speed ends exact.

Example: start at `v = 0.3 m/s`, target 0.6 m/s. Speeds after each step (m/s): deadbeat 0.31, 0.60, 0.60 (the first foot was set in advance); steps 1.5 times the deadbeat length 0.31, 0.42, 0.22, 0.67, -0.34 (negative = backward).

![Two walkers, one with steps too long](../assets/clip-example.mp4)

*Blue's steps are 1.5 times the deadbeat length: its feet jump forward and back and its body barely advances, while green walks at 0.6 m/s. Floor lines every 0.5 m.*

![What the step length does to speed](../assets/diagram-step-length-outcomes.png)

*Scale the deadbeat step by 0.6 and speed runs away. Scale it by 1.5 and the foot lands so far ahead that gravity pulls the body back: speed swings and reverses.*

In steady walking at `v_target` the deadbeat step settles at `2 Tc v tanh(T/2Tc)`. For `T = 0.4 s`, `h = 0.9 m` and `v = 0.6 m/s` that is 0.21 m.

![Centre of mass over six steps](../assets/fig-com-over-steps.png)

*Same start and target. Deadbeat steps lock the speed at 0.6 m/s from step 2. Steps scaled to 60% reach 5 m/s by step six.*

## Build It

```python
def next_foot(x, v, v_target, T, h):
    tc = time_constant(h)
    u = (v_target - v * np.cosh(T / tc)) * tc / np.sinh(T / tc)
    return x - u
```

`walk()` chains stances; `step_scale` multiplies the step length so you can break it.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/02-walking-by-foot-placement -q
python3 phases/10-legged-and-aerial/02-walking-by-foot-placement/code/main.py
```

## Use It

The last test checks the first stance against SciPy's integrator. Real controllers add step-time choice and swing-foot limits, and clamp the foot to reachable positions.

## Ship It

`outputs/skill-foot-placement-check.md` reviews a step controller for deadbeat consistency, step-length scaling and reach limits.

## Exercises

1. Clamp the step length to 0.15 m; find the fastest speed the walker can hold.
2. Change `T` to 0.6 s; recompute the steady step length.
3. Add 20 mm of error to the measured `x`; see how far the speed misses.
