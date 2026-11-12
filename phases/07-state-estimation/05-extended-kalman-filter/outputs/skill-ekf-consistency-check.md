---
name: ekf-consistency-check
description: Use when an extended Kalman filter drifts, jumps, or reports a covariance that looks too small, or before trusting a new EKF motion or measurement model. Checks Jacobians, angle wrapping and NEES.
---

# EKF consistency check

1. Compare every analytic Jacobian (motion `F`, measurement `H`) with central finite differences at 3 random states. A mismatch above 1e-5 is a bug.
2. Find every angle in the state or the innovation. Each difference must be wrapped to `[-pi, pi]` before it enters the gain.
3. Simulate with known truth over 100+ seeds and compute NEES `e^T P^-1 e`. The mean should be near the state dimension. Far above means overconfident: raise `Q` or `R`, or fix the model.
4. Repeat with the initial heading off by 0.5, 1.0 and 1.5 rad and with the fewest landmarks the real robot will see. Report where NEES leaves the consistent band.

Return the Jacobian error, the unwrapped angles found, the mean NEES per case and the first failing start. Never retune `Q` or `R` to hide a Jacobian error.
