---
name: impedance-check
description: Use when choosing or reviewing joint impedance gains (K, D) for a compliant or interaction task. Checks deflection budget, damping ratio and the host-loop sampling limit.
---

# Impedance gain check

1. Deflection: `x = F_max / K` must be inside the budget. Report `K_min = F_max / x_max`.
2. Damping ratio `zeta = D / (2 sqrt(K J))`. For a handover or contact task target 0.7 to 1. Below 0.4 expect visible overshoot, `exp(-pi zeta / sqrt(1 - zeta^2))`.
3. Sampling limit, using the lowest-inertia pose `J`: the update that `simulate()` uses stays stable only while `dt*dt*K/J + 2*dt*D/J < 4` (this includes `dt*D/J < 2`). The damper-only bound `dt*D/J < 1` for smooth motion does not certify a spring-and-damper loop; run the full check, or the eigenvalues of the 2x2 update matrix.
4. Confirm gravity feedforward matches the model at the task poses (see gravity-comp-check), or the rest pose will sag by residual / K.

Return a table `joint, K, D, J, zeta, deflection, r, verdict`. Never apply gains.
