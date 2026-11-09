---
name: computed-torque-check
description: Use when a model-based joint controller (computed torque, inverse-dynamics feedforward) is proposed or tuned, or when joint PD tracking degrades on fast motion. Checks the model terms, the error floor and the sampling limit.
---

# Computed-torque check

1. Verify the model before using it: `M` symmetric and positive definite, `M` against kinetic energy, `h` against energy conservation in free motion, and the whole `M qdd + h` against the engine's inverse dynamics (for example `mj_inverse` in simulation).
2. Compare against a joint PD of the same bandwidth on the real trajectory. Report max tracking error of both. If computed torque is not clearly better, suspect the model, not the gains.
3. Perturb the masses by 20% in simulation. Computed torque should still beat PD. If not, the loop depends on the model too much.
4. Computed torque inverts `M`. Check `kd` and `kp` against the sampling limit (`kd` below about `J/dt` for the smallest `M` eigenvalue).

Return max error for PD, exact model and perturbed model, plus the verdict. Never send commands to hardware.
