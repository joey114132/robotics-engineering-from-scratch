---
name: complementary-filter-check
description: Use when a tilt, roll or pitch estimate fuses a gyro with an accelerometer (complementary, Mahony or Madgwick style), or when an attitude estimate is too noisy or creeps away at rest. Checks the time constant against the measured gyro bias and accelerometer noise.
---

# Complementary filter check

1. Find the blend weight and convert it: `tau = a * dt / (1 - a)`. Report `tau`, `dt` and the crossover `1 / (2 pi tau)` Hz. Flag a weight that was set without a stated `dt`.
2. Measure the gyro bias `b` and the accelerometer tilt noise `s` with the robot still. Predict the steady tilt error `tau * b` and the noise standard deviation `s * sqrt(dt / (2 tau))`.
3. Compute the best `tau = (s^2 dt / (4 b^2))^(1/3)` and compare it with the one in the code. Within a factor of 2 is fine, because the error curve is flat near the minimum.
4. Check the accelerometer is only trusted when it measures gravity alone. During hard accelerations or shaking its tilt is wrong, so the weight should drop or the sample should be gated.
5. Check the gyro bias is not a fixed constant forever: it moves with temperature. A drifting estimate at rest means `tau` is too large for the current bias.
6. Check that the gyro rate and the accelerometer tilt are in the same frame, axis order and sign.

Return `tau`, the best `tau`, the predicted steady error and PASS or a list of `file:line` violations. Never edit.
