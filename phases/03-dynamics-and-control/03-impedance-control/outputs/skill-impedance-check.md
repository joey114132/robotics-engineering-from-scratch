---
name: impedance-check
description: Use when choosing or reviewing joint impedance gains (K, D) for a compliant or interaction task. Checks deflection budget, damping ratio and the host-loop sampling limit.
---

# Impedance gain check

1. Deflection: `x = F_max / K` must be inside the budget. Report `K_min = F_max / x_max`.
2. Damping ratio `zeta = D / (2 sqrt(K J))`. For a handover or contact task target 0.7 to 1. Below 0.4 expect visible overshoot, `exp(-pi zeta / sqrt(1 - zeta^2))`.
3. Sampling limit: `dt*D/J < 1` for smooth, `< 2` to stay stable, using the lowest-inertia pose.
4. Confirm gravity feedforward matches the model at the task poses (see gravity-comp-check), or the rest pose will sag by residual / K.

Return a table `joint, K, D, J, zeta, deflection, r, verdict`. Never apply gains.
