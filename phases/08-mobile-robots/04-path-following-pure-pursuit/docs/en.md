# Path Following with Pure Pursuit

> Aim at a point a fixed distance ahead on the path, and let that one distance trade wobble against cut corners.

**Type:** Build   **Prerequisites:** 08/01 Differential Drive and Odometry   **Time:** ~15 minutes

## The Problem

You give a mobile robot a path with a right-angle corner. With a short look-ahead it snakes along the straight parts, and with a long one it sails across the corner and hits whatever is standing there.

## The Concept

![One step of pure pursuit](../assets/diagram-pp-step.png)

*Pick the path point `Ld` ahead, measure how far it sits to the side of the robot, and steer along the circle that reaches it.*

Put the target in the robot frame, with side offset `y` and distance `d`. The circle that starts along the heading and passes through it has curvature `k = 2 y / d^2`, which a test checks against `2 sin(a) / d`. The turn rate is `w = v k`. The drive follows `w` through a first-order lag, because a real base cannot turn instantly. The 0.4 s time constant is our assumption, not a measurement.

![One knob, two failures](../assets/diagram-pp-tradeoff.png)

*A short `Ld` steers hard at a nearby point. A long `Ld` aims at a point that is far off the path near a corner.*

![Three look-ahead distances on the same path](../assets/fig-lookahead-paths.png)

*The robot starts 0.6 m left of the path at 1 m/s. At `Ld = 0.4 m` it crosses the line 10 times on the first straight and passes within 0.17 m of the corner. At 1.5 m it settles and passes 0.41 m away. At 4 m it has not settled by the corner and passes 1.37 m away.*

A test shows that the short look-ahead does not wobble without the lag, so the wobble is high gain meeting drive delay.

## Build It

```python
def curvature(pose, target):
    dx, dy = target - pose[:2]
    y = -np.sin(pose[2]) * dx + np.cos(pose[2]) * dy
    return 2 * y / (dx * dx + dy * dy)

def lookahead_point(path, pos, ld):
    i = np.linalg.norm(path - pos, axis=1).argmin()
    far = np.nonzero(np.linalg.norm(path[i:] - pos, axis=1) >= ld)[0]
    return path[i + far[0]] if len(far) else path[-1]
```

`follow()` runs the loop and returns the trajectory. `sign_changes()` counts line crossings.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/04-path-following-pure-pursuit -q
python3 phases/08-mobile-robots/04-path-following-pure-pursuit/code/main.py
```

## Use It

Nav2's regulated pure pursuit controller uses the same idea: it finds a point on the path in front of the robot and drives toward it. Its README says the choice of look-ahead depends on robot size, responsiveness, update rate and speed, and it offers a velocity-scaled look-ahead.

Sources: Nav2 `nav2_regulated_pure_pursuit_controller` README, github.com/ros-navigation/navigation2, opened 2026-11-09.

## Ship It

`outputs/skill-pure-pursuit-tuning.md` tunes `Ld` from a wobble count and a corner cut.

## Exercises

1. Scale `Ld` with speed and compare the wobble at 0.5 and 2 m/s.
2. Round the corner with a short arc in the path and measure the cut again.
3. Find the smallest `Ld` with at most 2 line crossings for a lag of 0.2 s.
