# Collision Checking

> A path that is checked only at sample points can tunnel through an obstacle thinner than the sample spacing.

**Type:** Build   **Prerequisites:** 09/02 RRT   **Time:** ~15 minutes

## The Problem

The planner reports a collision-free path, and the robot hits a post on the way. Every pose on the path was checked and every one was free. The post is thinner than the distance the arm moves between two checks, so the arm jumped over it in the checker's eyes and went straight through it in the real world.

## The Concept

![How a path tunnels](../assets/diagram-tunnel.png)

*A step larger than the obstacle width lets the samples land on both sides of it.*

A point is inside a circle when its distance to the centre is at most `r`. A segment hits the circle when its closest point to the centre is inside. That closest point is found by projecting the centre onto the segment and clamping to the ends, so the test is exact.

A swept check tests only points spaced at most `s` apart along the segment.

![Two step sizes, and miss rate against step](../assets/fig-tunnelling.png)

*Left: the coarse step misses the obstacle and the fine step catches it. Right: the larger the step, the more real hits are missed.*

![Choosing the step size](../assets/diagram-step-rule.png)

*A step of at most `2r` catches every crossing through the centre. Padding by `s/2` catches all crossings.*

The chord through the centre is `2r` long, so a step of at most `2r` puts a sample on it. A grazing segment has a short chord and can still slip through. Every point of the segment is within `s/2` of a sample, so growing the circle by `s/2` never misses a hit. The price is false alarms, the dashed line in the figure.

## Build It

```python
def conservative_hits(a, b, c, r, step):
    return swept_hits(a, b, c, r, step, pad=step / 2)
```

`swept_hits` places `ceil(length / step) + 1` samples on the segment. The tests compare it with the exact test on thousands of random segments.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/03-collision-checking -q
python3 phases/09-motion-planning/03-collision-checking/code/main.py
```

## Use It

SciPy's `minimize_scalar` finds the closest point numerically. The last test compares it with the closed-form test on random segments.

Sources: [Motion planning, Wikipedia](https://en.wikipedia.org/wiki/Motion_planning) (opened 2026-11-09: collision detection tests whether the robot's geometry collides with the environment's geometry, and grid approaches require setting a grid resolution).

## Ship It

`outputs/skill-collision-step-check.md` audits a planner's collision resolution against its thinnest obstacle.

## Exercises

1. Find the smallest `step` for which the padded check has under 5% false alarms.
2. Pad by the exact worst-case gap `length / (2n)` and compare false alarms.
3. Extend `seg_hits` to a moving circle robot by adding its radius to `r`.
