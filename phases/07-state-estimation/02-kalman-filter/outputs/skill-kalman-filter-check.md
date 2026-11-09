---
name: kalman-filter-check
description: Use when writing, tuning or reviewing a Kalman filter (linear, extended or unscented) for a robot state estimate, or when an estimate lags, jitters or reports a covariance that does not match the real error. Checks the model, Q, R and consistency.
---

# Kalman filter check

1. State the model: what is in `x`, what `F` assumes (constant velocity? constant position?), and what `H` observes. Flag states that are never observed and have no model noise.
2. Check units and sources of `Q` and `R`. `R` should come from a sensor spec or measured scatter, `Q` from how much the real motion departs from the model. Flag values that were only tuned until the plot looked good.
3. Check the update uses the innovation `z - H x` and a gain from the covariance. Flag a fixed gain unless the code says it is a steady-state value.
4. Check `P` stays symmetric and positive: use the Joseph form or symmetrise after each update.
5. Test consistency, not only error: over repeated runs the real error covariance must match `P`, about 95% of errors must lie inside 2 sigma, and the mean normalised error squared must be near the state dimension.
6. If the filter is over-confident (coverage below 95%) raise `Q` or `R`. If it lags and the coverage is near 100%, lower them.

Return PASS or a list of `file:line` findings. Never change gains on a real robot.
