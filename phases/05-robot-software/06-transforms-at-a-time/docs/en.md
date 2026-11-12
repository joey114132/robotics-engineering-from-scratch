# Transforms at a Time

> A transform lookup is a question about one instant, so the buffer must interpolate between samples or refuse to answer.

**Type:** Build   **Prerequisites:** 01/04 Frames and Transform Trees, 05/04 Time Sync and Traces   **Time:** ~15 minutes

## In Plain Words

Make a panorama while turning with your phone. Each slice sees the room from a different direction. If you
place every slice as though it were taken facing the final direction, the pieces no longer line up with the
room.

A moving scanner has the same problem. Each measured point needs the transform at its own timestamp. A buffer
interpolates between stored poses for that time. Using the newest pose for every point instead can bend a
straight wall in the reconstructed scan.

## The Problem

A laser scan takes half a second while the robot turns. You place every point with the newest pose, because that is the easy lookup. A straight wall comes out bent, and the faster the robot turns the worse it gets. The scan points carry the times they were measured, and the lookup ignored them.

## The Concept

![Which pose places a scan point](../assets/diagram-scan-stamps.png)

*Each point should be placed with the pose at its own stamp. The newest pose is right for only the last point.*

A transform tree (01/04) answers "where is frame B in frame A". Add time and the question becomes "where was B in A at time t". Poses arrive at discrete times, so the buffer has three cases.

![Three answers for one lookup](../assets/diagram-lookup-rules.png)

*Between two samples it interpolates. Slightly past the newest it may extrapolate within a set limit. Anything else raises an error.*

Position is a plain lerp. Orientation uses the slerp from 01/03, which also fixes a flipped quaternion sign. Refusing is a feature: a guess past the newest sample looks like data and hides a late message.

![Smeared and stamped scans](../assets/fig-scan-smear.png)

*Left: a straight wall scanned for 0.5 s while turning 1 rad/s. Right: the newest-pose error grows with turn rate and starts at 0.25 m from driving alone. The stamped error stays at zero.*

## Build It

```python
i = min(bisect.bisect_right(self.t, t) - 1, len(self.t) - 2)
a = (t - self.t[i]) / (self.t[i + 1] - self.t[i])
return (1 - a) * self.p[i] + a * self.p[i + 1], slerp(self.q[i], self.q[i + 1], a).copy()
```

`lookup()` raises `LookupError` for a time older than the oldest sample or newer than the newest plus `max_extrapolation`. `add()` accepts late samples in any order and drops history beyond `window`. `to_world()` places scan points with stamped or newest poses.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/06-transforms-at-a-time -q
python3 phases/05-robot-software/06-transforms-at-a-time/code/main.py
```

## Use It

The tf2 buffers in ROS 2 answer the same question and raise an extrapolation exception for the same reason. Read the tf2 "Using time" tutorial, then ask a buffer for a pose slightly in the future and see what it does.

## Ship It

`outputs/skill-timed-transform-check.md` checks that sensor data is placed with the pose at its own stamp.

## Exercises

1. Set `max_extrapolation = 0.1` and find the largest turn rate where the guess stays under 1 cm.
2. Feed samples at 10 Hz and 100 Hz and compare the midpoint error for a robot that accelerates.
3. Add a second buffer for another frame and compose the two lookups at one stamp.
