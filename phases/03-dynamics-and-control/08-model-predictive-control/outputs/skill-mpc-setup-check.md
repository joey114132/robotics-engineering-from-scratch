---
name: mpc-setup-check
description: Use when setting up or reviewing a model predictive controller (horizon, weights, terminal cost, input limits, solver) or when a clipped controller overshoots at its actuator limit.
---

# MPC setup check

1. Confirm the limit is inside the optimisation as a constraint, not clipped after it.
2. Check the terminal cost. Without one, a short horizon is myopic. LQR's P is a safe default for a linear model.
3. With the limits loosened, the first input must equal the LQR action. If not, the prediction model or weights are wrong.
4. Vary N on a worst-case start and report the cost. Pick the smallest N within a few percent of the best.
5. Time one solve at the worst case against the control period. Warm-start from the previous plan.
6. Say what happens when the solver does not converge: the fallback must be a safe command, not the last one.

Return N, weights, terminal cost, overshoot against a clipped baseline and the worst solve time. Never change limits on hardware.
