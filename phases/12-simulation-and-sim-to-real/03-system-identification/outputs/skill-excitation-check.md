---
name: excitation-check
description: Use before fitting plant parameters (inertia, friction, damping, motor lag) from a recorded trajectory, or when a fitted simulator matches one run and misses the next. Checks whether the recording can identify each parameter.
---

# Excitation check

1. Write the model as `dw = sum(theta_i * regressor_i)` over windows and build the regressor matrix before solving anything.
2. Normalise each column and compute the condition number. Above about 100, some combination is barely constrained: do not report those parameters one by one.
3. Check speed range and sign changes. A constant-speed run sees only `b*w0 + c`. Add speed changes and reversals so viscous and Coulomb terms separate.
4. Put nonlinear parameters (motor lag) on a grid around the linear solve and keep the lowest residual. Ignoring a real lag leaves a visibly larger residual.
5. Fit on one recording, validate on another with different commands. Quote each parameter with its error (repeat over noise seeds).

Return the condition number, the fitted values with error bars and the one extra trajectory that would remove the biggest uncertainty. Never present a single-trajectory match as proof.
