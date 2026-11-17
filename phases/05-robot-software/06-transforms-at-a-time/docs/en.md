# Transforms at a Time

> Learn why a turning robot's laser scan bends a straight wall, and how timestamps fix it.

**Type:** Build   **Prerequisites:** 05/04 Time Sync and Traces   **Time:** ~15 minutes

## In Plain Words

A rover turns while its laser scans a straight wall. The rover turned a little between points, so each point needs the rover's pose at its own time. A pose buffer stores past poses and fills the gaps. Use the newest pose for every point and the wall bends.

## Key Terms

- **Frame**: a coordinate system attached to a body, such as the rover or the laser.
- **Pose**: a body's position and direction at one moment.
- **Transform**: where one frame sits and which way it points, measured from another frame.
- **Time stamp**: the moment a measurement was taken.
- **Interpolate**: estimate a value between two known samples.
- **Extrapolate**: guess a value past the newest sample by continuing the last motion.

## The Problem

A rover's laser scans a straight wall while the rover turns. Using the newest pose for every point bends the wall.

## The Concept

A robot must know where its body was at the instant of each measurement.

![Which pose places a scan point](../assets/diagram-scan-stamps.png)

*The newest pose fits only the last point. The pose at the stamp keeps the wall straight.*

A transform tree (how the robot's parts are placed relative to each other) says where one part is as seen from another. Add time and it says where it was at that instant. The buffer answers in three ways. Between two stored poses it blends them (interpolates). A little past the newest it may guess (extrapolates), within a limit. Anything else is an error.

![Three answers for one lookup](../assets/diagram-lookup-rules.png)

*Between samples: blend. Slightly past the newest: guess within a limit. Else: error.*

![Interpolated answer and a refusal](../assets/clip-example.mp4)

*Grey ghosts are stored poses. Amber is a moment between them. The red cross is too new and is refused.*

![Smeared and stamped scans](../assets/fig-scan-smear.png)

*Right: the newest-pose error grows with the turn rate, while the stamped error stays at zero.*

<details><summary>The math (optional)</summary>

Position is a lerp (straight-line blend). Orientation uses the slerp from 01/03, a blend of two rotations along the shortest arc. The guess limit is 0 s by default. Refusing is a feature: a guess would hide that data arrived late. Poses at 0 s and 1 s are 1.2 m and 1 rad apart. A lookup at 0.5 s answers 0.6 m and 0.5 rad. At 1.5 s it raises `LookupError`: 0.500 s past the newest sample, and the limit is 0. The wall is scanned for 0.5 s while turning 1 rad/s.

</details>

## Build It

```python
i = min(bisect.bisect_right(self.t, t) - 1, len(self.t) - 2)
a = (t - self.t[i]) / (self.t[i + 1] - self.t[i])
return (1 - a) * self.p[i] + a * self.p[i + 1], slerp(self.q[i], self.q[i + 1], a).copy()
```

`lookup()` raises `LookupError` for a time outside the stored poses, allowing `max_extrapolation` past the newest. `to_world()` places scan points with stamped or newest poses.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/06-transforms-at-a-time -q
python3 phases/05-robot-software/06-transforms-at-a-time/code/main.py
```

## Use It

ROS 2's transform library, tf2, raises an error for the same reason.

## Ship It

`outputs/skill-timed-transform-check.md` checks that sensor data uses the pose at its stamp.

## Exercises

1. Raise `max_extrapolation` a little and see when the guess stays good.
2. Feed poses more slowly and compare the midpoint error.
3. Make two `PoseBuffer`s (one per frame) and combine their answers at one stamp.
