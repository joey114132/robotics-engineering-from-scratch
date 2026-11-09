---
name: odometry-calibration-check
description: Use when wheel odometry of a differential-drive robot drifts, a loop does not close, or after a wheel or track change. Turns a measured closure gap into a suspected parameter and a calibration run.
---

# Odometry calibration check

1. Drive a square of known side (2 m or more) in both directions with the same wheel commands. Measure the real start-to-end gap with a tape or a fixed reference, not with odometry.
2. Compare the gap size with the odometry loop closure. Both a track width error and a radius error open the loop, so also run step 3 to separate them.
3. Drive a straight line of 3 m. If it bends, the two wheel radii differ. If only its length is off, scale `r`.
4. Fix one parameter at a time and rerun the square. Stop when the gap is inside the sensor noise.

Return the measured gap per direction, the suspected parameter and the run to confirm it. Never edit the config yourself.
