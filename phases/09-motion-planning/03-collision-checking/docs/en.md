# Collision Checking

> Learn why checking a path at only a few spots can miss a thin obstacle, and how to check safely.

**Type:** Build   **Prerequisites:** 09/02 RRT   **Time:** ~15 minutes

## In Plain Words

A toy car drives past a thin post. A checker plants pegs along the route and asks at each if the car is in the post. Pegs spaced wider than the post can all land beside it, so every peg says free while the car hits the post between them.

Testing the whole stretch catches the hit. So does pretending the post is wider, but then safe routes get rejected.

## Key Terms

- **Collision checking**: testing whether a robot pose or motion touches an obstacle.
- **Tunnelling**: a motion slipping through a thin obstacle because the checks are too far apart.
- **Segment**: the straight stretch between two path points.
- **Chord**: the part of a segment that lies inside a circle.
- **Padding**: growing the obstacle by a margin so the check errs on the safe side.
- **False alarm**: a hit reported for a path that actually clears the obstacle.

## The Problem

Picture a robot arm whose planner reports a collision-free path, yet it hits a thin post. Every checked pose was free; the post is thinner than the move between checks.

## The Concept

A real robot hits whatever its checker skips, so check spacing must match the thinnest obstacle.

![Tunnelling](../assets/diagram-tunnel.png)

*A wide step lets samples land on both sides.*

Seen from above, a post is a circle of radius `r`. A segment hits it when its point closest to the centre is inside. That point is the centre's projection, clamped to the ends, so this test is exact. A swept check tests only points at most `s` apart.

![Step sizes](../assets/fig-tunnelling.png)

*Coarse steps miss, fine steps catch.*

![Step rule](../assets/diagram-step-rule.png)

*A step of at most `2r` catches centre crossings; padding by `s/2` catches all.*

A chord through the centre is `2r` long, so a step of at most `2r` puts a sample on it, but a grazing segment can slip through. Growing the circle by `s/2` never misses, at the price of false alarms.

Take `r = 0.25`, a peg every `0.5 = 2r`, and a segment passing 0.2 from the centre. Two pegs sit 0.25 either side of the closest point, each 0.32 from the centre, so the plain check says free while `seg_hits` says hit. Padding by `s/2 = 0.25` catches both.

![Two cars](../assets/clip-example.mp4)

*Blue's pegs stay white; it clips the post. Green's turn red; it stops.*

## Build It

```python
def conservative_hits(a, b, c, r, step):
    return swept_hits(a, b, c, r, step, pad=step / 2)
```

`swept_hits` places `ceil(length / step) + 1` samples on the segment. Tests compare it with the exact test.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/03-collision-checking -q
python3 phases/09-motion-planning/03-collision-checking/code/main.py
```

## Use It

SciPy's `minimize_scalar` finds the closest point numerically; a test compares it.

Sources: [Motion planning, Wikipedia](https://en.wikipedia.org/wiki/Motion_planning) (opened 2026-11-09).

## Ship It

`outputs/skill-collision-step-check.md` audits a planner's collision step against its thinnest obstacle.

## Exercises

1. Find the smallest `step` with under 5% false alarms when padded.
2. Pad by the exact worst-case gap `length / (2n)`; compare false alarms.
3. Add a circle robot's radius to `r`.
