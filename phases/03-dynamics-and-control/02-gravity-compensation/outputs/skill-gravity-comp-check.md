---
name: gravity-comp-check
description: Use when an arm sags or floats at low position gain (compliance, soft modes), or when changing a gravity-compensation model. Converts measured sag into a model-error estimate.
---

# Gravity-compensation check

1. Hold the arm at 2 or more poses, one near horizontal, with the same low `kp`. Record `q - q_des` per joint after it settles.
2. Residual torque per joint is about `-kp * sag`. Negative sag (droop) means the feedforward is too small.
3. Fit one mass scale per link. Predict the sag at a different `kp`. If the prediction is off by more than 15%, the error is not a pure mass scale: suspect centre of mass, friction or a wrong sign.
4. Never close the gap by lowering `kp` further or by adding integral gain without saying so.

Return per-joint sag, residual torque, the fitted scale and its direction. Never change gains.
