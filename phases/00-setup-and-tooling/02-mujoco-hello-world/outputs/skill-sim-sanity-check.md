---
name: sim-sanity-check
description: Use when a new simulation, physics loop or MJCF model is about to be trusted, or after changing dt, integrator or model parameters. Checks period, energy and step-size convergence against a closed-form case.
---

# Simulation sanity check

1. Pick a case with a closed-form answer (pendulum period, free fall, mass-spring frequency). Run the simulation and compare. A mismatch above 1% means a setup mistake until proven otherwise: length, axis, units or gravity sign.
2. With no damping and no input, energy must stay bounded. Steady growth points at an explicit integrator or a too-large `dt`.
3. Halve `dt` and rerun. The result should move by about the expected power of `dt`. If it does not move, something else limits accuracy.
4. If a second simulator is available, run the same case in both and compare.

Report the closed-form value, the measured value, the relative error, the `dt` used and the energy ratio at the end. Do not tune parameters to force agreement.
