---
name: watchdog-budget
description: Use when choosing or reviewing a heartbeat timeout, a command-loss stop or an emergency deceleration for a joint or axis. Checks the timeout against the stopping-distance budget and the heartbeat period.
---

# Watchdog budget

1. Write down the worst-case speed `v`, the deceleration `a` the drive can really deliver, and the room to the nearest limit at that speed.
2. Stopping distance is `v^2 / (2a)`. If it alone exceeds the room, no timeout works: lower `v` or fix the limit.
3. Upper bound on the timeout: `T <= (room - v^2 / (2a)) / v`. Subtract the control period and the heartbeat period for a safety margin.
4. Lower bound: the heartbeat period plus the worst observed jitter. Below it, one late message trips the watchdog.
5. Check what the stop action is. Zero torque on a joint without a brake coasts, so it is not a stop. Prefer a ramp, or a brake that is verified to hold.

Return the two bounds, the chosen timeout and the numbers behind it. State which values were measured and which were assumed.
