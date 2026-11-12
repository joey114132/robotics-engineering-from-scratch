---
name: timed-transform-check
description: Use when sensor data (scans, point clouds, camera frames) is placed in another frame while the robot moves, when a map looks smeared during turns, or when a transform lookup uses "latest" instead of a stamp. Checks stamped lookups, interpolation and refusal.
---

# Timed transform check

1. For each sensor consumer, find the time it asks for: the message stamp, or the newest pose. Flag every "latest" lookup on data that took time to capture.
2. Confirm the pose buffer interpolates between samples (lerp for position, slerp for orientation) and returns the stored pose exactly at a sample.
3. Confirm a query older than the oldest sample, or newer than the newest plus the extrapolation limit, raises an error that names the gap in seconds.
4. Replay a turn at 1 rad/s over the scan duration. Report the worst point error for stamped and newest-pose placement.
5. Check that late and out-of-order samples are stored by stamp, and that the window is longer than the largest sensor delay.

Return the lookups that use the wrong time, the worst error in meters and the extrapolation limit in seconds. Never raise the limit to hide a refused lookup; report the missing message.
