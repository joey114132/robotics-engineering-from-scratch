---
name: capture-point-check
description: Use when reviewing or writing balance code for a legged robot, or deciding whether a push needs a step. Checks the ZMP limit, the capture-point test and the step trigger against the inverted-pendulum model.
---

# Capture-point check

1. Find the model height `h` and compute `Tc = sqrt(h/g)`. Reject any hard-coded time constant that does not match.
2. Compute `xi = x + v*Tc` from the measured centre of mass. Compare it with the support area, with a margin for state error.
3. If `xi` is inside, the ankle or ZMP controller may hold. The commanded ZMP must be clamped to the support area.
4. If `xi` is outside, a step is required. The foot target is `xi` at landing time, not at the time of the decision. Include the swing delay.
5. Flag code that lets the ZMP command leave the foot, or that keeps pushing with the ankle after saturation.

Return the model height, `Tc`, `xi`, the support limits, the decision (hold or step) and the step target. Never send commands.
