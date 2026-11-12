# Mobile Navigation in Simulation

> A planner draws the route, but the robot only follows where it believes it is, so a drifting odometry estimate turns a good plan into a crash.

**Type:** Build   **Prerequisites:** 08/01 Differential Drive, 08/04 Pure Pursuit, 09/03 Collision Checking   **Time:** ~30 minutes

## In Plain Words

Your phone sketches your school walk from counted steps and turns. If those estimates drift, it may show you beside the right corridor
while you are beside another. Following a good route from that wrong starting belief sends you the wrong way.

This navigation system plans around obstacles, then steers using an estimated pose. Biased wheel readings separate that estimate from
the real robot. Observing known landmarks corrects position and heading, so the same follower can use the route successfully again.

## The Problem

The planner found a clean route and the follower tracks it well in tests. On a longer run the robot ends up metres from the goal, pressed against a wall, while its own display says it is on the path. The plan was fine. The belief was wrong.

## The Concept

![Parts of the navigation system](../assets/diagram-nav-system.png)

*A grid is inflated by the robot radius, A\* finds a route, shortcuts trim it, and pure pursuit steers a differential-drive robot from its odometry estimate.*

![Break test diagram](../assets/diagram-nav-broken.png)

*Odometry error grows the longer the robot drives. A landmark fix resets it before it matters.*

![The task succeeding](../assets/fig-nav-result.png)

*A\* gives 77 waypoints and 21.1 m. Shortcuts keep 6 waypoints and 19.8 m. With small odometry error the robot ends 0.28 m from the goal without touching a wall.*

![Drift with and without the fix](../assets/fig-nav-drift.png)

*Without a fix the belief ends 4.7 m from the truth and the robot hits a wall. With a fix once per second the belief stays within 0.11 m and the goal error is 0.15 m.*

## Build It

The robot steers from `est`, while the true pose moves as commanded. Wheel readings carry a speed error, a turn-rate bias and noise.

```python
vm = v * (1 + scale_err) + rng.normal(0, sigma)
wm = w + w_bias + rng.normal(0, sigma)
est = est + dt * np.array([vm * np.cos(est[2]), vm * np.sin(est[2]), wm])
```

`pose_fix()` recovers the pose from two landmarks seen in the robot frame: heading from the direction between them, position from the first. Walls do not block the beacons in this model.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/16-capstones/02-mobile-navigation-sim -q
python3 phases/16-capstones/02-mobile-navigation-sim/code/main.py
```

## Use It

ROS 2 Nav2's NavFn planner has a `use_astar` parameter: "Whether to use A*. If `false`, uses Dijkstra's expansion." Run both searches on this grid and compare the paths.

Sources: [Nav2 NavFn planner configuration](https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/planners_plugins/configuring_navfn/), read 2026-11-09.

## Ship It

`outputs/skill-nav-drift-triage.md` separates a bad plan from a bad pose estimate when a robot misses its goal.

## Exercises

1. Hide the beacons for the first half of the run and measure the drift before the first fix.
2. Replace the two-landmark fix with a range-only fix to one landmark and see what stays unknown.
3. Widen the inflation radius to 0.6 m and check that the planner still finds a route.
