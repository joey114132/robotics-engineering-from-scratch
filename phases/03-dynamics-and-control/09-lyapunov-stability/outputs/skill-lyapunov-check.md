---
name: lyapunov-check
description: Use when someone claims a controller is stable only because a simulation settled, or when a gain, delay or filter change needs a stability argument for a nonlinear plant.
---

# Lyapunov check

1. Propose a candidate V: usually kinetic energy plus the potential energy of gravity and of the control springs. Confirm it is zero at the goal and positive elsewhere.
2. Compute dV/dt along the dynamics, by hand where possible. Cancel what cancels. Report what is left, such as -(c + kd) w^2.
3. Sample states across the whole operating range, including corners and high speed. Report the largest dV/dt and the state where it occurs.
4. Repeat with the real delay, filter and saturation. Anything the controller uses that is not in the state breaks the test; simulate it and watch V.
5. State the limit: sampling finds counterexamples and does not prove stability.

Return the V used, the dV/dt expression, the worst sampled slope and its state, and the delayed-run result. Never change gains on hardware.
