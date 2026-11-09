---
name: trajectory-profile-check
description: Use when reviewing or writing a point-to-point joint trajectory (cubic, quintic, trapezoid, or any time-scaled spline) before it is sent to a controller. Checks boundary conditions and the jerk the controller will see.
---

# Trajectory profile check

1. List the boundary conditions the profile enforces at start and end: position, velocity, acceleration. A cubic enforces the first two only.
2. Evaluate acceleration at `t = 0` and `t = T`. If either is nonzero, or the move starts from a controller at rest, the profile has an acceleration step.
3. Compute peak jerk as `max|diff(acc)| / dt` with zeros padded before and after, at the real control period. Compare it with the joint's jerk or torque-rate limit.
4. If the move time changes, rescale: velocity goes as `1/T`, acceleration as `1/T^2`, jerk as `1/T^3`.
5. Prefer a quintic or higher when the controller or gearbox cannot take a step in acceleration. A trapezoid is acceptable only with a stated acceleration limit and a controller that tolerates the steps.

Return the conditions enforced, the acceleration at both ends, the peak jerk at the control period, and a pass or fail against the stated limit. Never change the limit to make a profile pass.
