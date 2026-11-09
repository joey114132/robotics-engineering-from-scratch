---
name: pid-tuning-check
description: Use when PID gains on a joint are raised or lowered, when a joint oscillates or sits off target under load, or when an actuator can saturate. Reviews offset, windup and the host-loop stability limit.
---

# PID tuning check

1. Offset: with P (and D) only, a constant load leaves `load / kp`. If the task needs zero offset, `ki` must be nonzero, and the load must be bounded.
2. Windup: if the actuator can saturate (torque or current limit), the integrator must stop while saturated and the error pushes deeper. Check that the code does this.
3. Stability: build the closed-loop update matrix for the real `dt`, `J` (lowest-inertia pose), friction, `kp`, `kd`. Spectral radius below 1 is required. `kd` above about `2J/dt` flips the command every tick.
4. Raise gains one at a time and record the radius before and after. Never raise `kp` and `kd` together without that check.

Return a table `joint, kp, ki, kd, J, dt, offset, radius, verdict`. Never apply gains.
