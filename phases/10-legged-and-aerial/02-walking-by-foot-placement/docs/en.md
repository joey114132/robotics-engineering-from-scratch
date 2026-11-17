# Walking by Foot Placement

> Learn how a walking robot controls its speed just by choosing where each foot lands.

**Type:** Build   **Prerequisites:** 10/01 Inverted Pendulum and ZMP   **Time:** ~15 minutes

## In Plain Words

You control walking speed with where each foot lands. Put a foot well ahead and your body stays behind it. Gravity pulls you back, so you slow down. Put a foot too close and your body passes over it. Gravity pulls you forward, so you speed up.

A walking model picks each spot from the body's position and speed.

## Key Terms

- **Foot placement**: choosing where the next foot lands in order to control speed.
- **Stance**: the time one foot stays on the ground.
- **Touchdown**: the moment a swinging foot lands.
- **Deadbeat**: a rule that hits the target speed in one step and stays there.
- **Time constant (`Tc`)**: how quickly the body tips over, the same number as in lesson 01.

## The Problem

Picture a walking robot told to walk at a steady speed with a plausible fixed step. It speeds up every step until its body is far ahead of its feet. The steps were a little short.

## The Concept

A real walker has no brakes, only feet, so where a foot lands is how it speeds up or slows down.

At the end of each step the robot looks at where its body is and how fast it moves, then picks the next foot spot so the next step ends exactly at the target speed. This is called deadbeat.

![Loop](../assets/diagram-foot-placement-loop.png)

*At each step: read, pick the next foot.*

A foot placed well ahead leaves the body behind it, and gravity slows the body. A foot placed too close lets the body pass over it, and gravity speeds it up. Steps that are too long make the speed swing and even reverse.

![Two walkers](../assets/clip-example.mp4)

*Blue's steps are too long and it barely advances. Green walks steadily.*

![Outcomes](../assets/diagram-step-length-outcomes.png)

*Too short: speed runs away. Too long: speed swings.*

![Speed over steps](../assets/fig-com-over-steps.png)

*With the right steps, the speed settles from the second step.*

<details><summary>The math (optional)</summary>

Stance lasts `T` and the next foot sits at `p`. Let `u = x - p` be how far the body is ahead of that foot at touchdown. Lesson 01's model gives the speed at the end of the stance: `v' = (u/Tc) sinh(T/Tc) + v cosh(T/Tc)`, where `sinh` and `cosh` are curves built from `exp(t/Tc)` that describe the falling body. Setting `v' = v_target` and solving for `u` gives the foot, `p = x - u`. Start at 0.3 m/s with target 0.6 m/s. Deadbeat speeds after each step (m/s): 0.31, 0.60, 0.60 (the first foot was set in advance). Steps 1.5 times too long give 0.31, 0.42, 0.22, 0.67, -0.34. Steps scaled by 0.6 reach 5 m/s by step six. In steady walking the deadbeat step is `2 Tc v tanh(T/2Tc)`: 0.21 m for `T = 0.4 s`, `h = 0.9 m`, `v = 0.6 m/s`.

</details>

## Build It

```python
def next_foot(x, v, v_target, T, h):
    tc = time_constant(h)
    u = (v_target - v * np.cosh(T / tc)) * tc / np.sinh(T / tc)
    return x - u
```

`walk()` chains steps. `step_scale` multiplies the step length so you can break it.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/02-walking-by-foot-placement -q
python3 phases/10-legged-and-aerial/02-walking-by-foot-placement/code/main.py
```

## Use It

The last test checks the first step against a ready-made SciPy solver.

## Ship It

`outputs/skill-foot-placement-check.md` reviews a foot-placement rule for deadbeat consistency and reach limits.

## Exercises

1. Make the steps longer or shorter and watch the speed.
2. Limit the step length and find the fastest speed the walker can hold.
3. Make the measured body position a little wrong and see how far the speed misses.
