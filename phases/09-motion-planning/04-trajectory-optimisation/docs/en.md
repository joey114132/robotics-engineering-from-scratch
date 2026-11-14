# Trajectory Optimisation

> A planner's path is feasible but jagged. Gradient descent on a smoothness cost and an obstacle penalty turns it into a path a robot can follow.

**Type:** Build   **Prerequisites:** 09/03 Collision Checking   **Time:** ~15 minutes

## In Plain Words

A rover's route is a chain of waypoints pinned at the start and the flag, like a rubber band with cups in the way. The band's tension pulls each waypoint toward the straight line between its two neighbours, which smooths the route. A cup pushes any waypoint near it outward.

The route settles where pull and push balance. Moving the waypoints a little at a time lowers the total cost, a score of how bad the route is. Moving them too far overshoots the balance and raises it.

## The Problem

A sampling planner hands you a path that avoids every obstacle but zigzags. Following it wastes time and shakes the arm. Straightening the zigzag by hand puts the path back inside an obstacle, so the two goals fight each other.

## The Concept

![Smoothness plus obstacle penalty](../assets/diagram-cost-loop.png)

*Follow the numbers. Waypoints have fixed ends; two cost terms, smoothness and obstacle penalty, give one gradient that moves them.*

Smoothness is half the sum of squared steps between neighbours. Its gradient, the direction in which cost rises fastest, is `2 x_i - x_{i-1} - x_{i+1}` at a waypoint, so stepping against it pulls the point toward the line through its neighbours. The obstacle penalty is `w (r + margin - d)^2` when a waypoint is closer than `r + margin` to a centre (`w` = 8 is the penalty weight and `margin` is spare clearance), and zero otherwise. Stepping against its gradient pushes the point out. Repeating such steps (size `lr` = 0.04) is gradient descent.

![Two forces on every waypoint](../assets/diagram-two-forces.png)

*The path settles where the pull and the push balance. A step that is too large overshoots it and the cost goes up.*

Worked example: one waypoint between pins at (0, 0) and (10, 0), a cup of radius 1 at (5, 0), `margin = 0.4`. It starts at (5, 0.2), inside the cup. Smoothness pulls it down with 0.4 and the cup pushes it up with 19.2. After 8 steps it rests at (5, 1.24), where both forces are 2.49, 0.24 outside the cup.

![Pull and push on one waypoint](../assets/clip-example.mp4)

*Close-up of the route's middle, 0.8 m per unit. Watch the red arrows, pull down and push up (length grows with the square root of the force). The push starts huge and shrinks until they match. Then the rover drives.*

![Path before and after, and cost per iteration](../assets/fig-before-after.png)

*Left: the jagged start runs through both obstacles, the result bends around them. Right: cost falls every iteration.*

This is a small version of the CHOMP planner. It penalises waypoints only, not the segments between them.

## Build It

```python
g[1:-1] = ws * (2*X[1:-1] - X[:-2] - X[2:])
g[1:-1] -= 2 * wo * np.maximum(0, r + margin - d) * v / d
X -= lr * g
```

The endpoints get zero gradient, so they never move. A test compares the analytic gradient with finite differences.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/04-trajectory-optimisation -q
python3 phases/09-motion-planning/04-trajectory-optimisation/code/main.py
```

## Use It

SciPy's `minimize` with `method="L-BFGS-B"` takes the same cost and gradient. The last test checks that it reaches a cost no worse than 4000 plain steps.

Sources: [CHOMP, Ratliff et al. 2009](https://www.ri.cmu.edu/pub_files/2009/5/icra09-chomp.pdf) (opened 2026-11-09).

## Ship It

`outputs/skill-path-smoothing-check.md` reviews a smoothed path for clearance, endpoints and step size.

## Exercises

1. Raise `margin` to 0.8 and report how the closest approach changes.
2. Check the segments between waypoints with the exact test from lesson 03 and report the smallest clearance.
3. Use `scipy.optimize.minimize` and compare iterations with plain descent.
