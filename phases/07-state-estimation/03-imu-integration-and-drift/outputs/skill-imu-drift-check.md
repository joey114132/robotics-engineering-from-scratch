---
name: imu-drift-check
description: Use when an estimate relies on integrating a gyro or accelerometer (dead reckoning, attitude, visual-inertial gaps, GPS outages), or when a stationary IMU's angle or position drifts. Estimates how long the integrated result stays usable and which reference must correct it.
---

# IMU drift check

1. Record the IMU stationary for a few minutes. Read the mean of each gyro and accelerometer axis: that is the bias. The scatter, scaled by `sqrt(dt * t)`, gives the random-walk term.
2. Predict the error at time `t`: angle `b t`, velocity `a t`, position `a t^2 / 2`. Add the tilt leak `g b t^3 / 6` when the angle feeds a gravity subtraction.
3. State the time when each error reaches the tolerance the task needs (for example 1 degree or 0.1 m). That is how long the result can go uncorrected.
4. Check what corrects it. Gyro drift needs an absolute reference (gravity direction, a magnetometer, vision). Position drift needs a position or velocity reference. Averaging or a higher sample rate corrects nothing.
5. Check that bias is estimated or re-measured at rest, and that the stationary mean is not removed once and then trusted for hours (bias moves with temperature and time).
6. Flag any code that integrates the accelerometer without first removing gravity using the current orientation estimate.

Return the drift budget (error per axis versus time) and PASS or a list of `file:line` violations. Never edit.
