---
name: hand-eye-check
description: Use when planning or reviewing a hand-eye calibration (camera on a gripper or fixed camera), or when a calibrated camera-to-gripper transform gives targets that are consistently off. Checks axis diversity and residuals.
---

# Hand-eye check

1. List the rotation axes of the calibration motions (axis of each relative gripper rotation). Compute the SVD of the stacked axis correlation matrix.
2. If the second singular value over the first is below about 1e-2, the axes are nearly parallel. Add motions about other axes before calibrating.
3. After solving, compute the residual of `A X - X B` per motion. One large residual means a bad pose detection, not a bad solver.
4. Translation along a single common rotation axis is unobservable. Do not trust that component if the motions had one axis.
5. Use at least 3 poses, and many more for noisy detections.

Return the singular-value ratio, per-motion residuals, rotation and translation spread, and a pass or fail. Never command the robot; only propose motions.
