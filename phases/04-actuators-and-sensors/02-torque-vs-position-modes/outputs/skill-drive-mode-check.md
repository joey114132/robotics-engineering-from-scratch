---
name: drive-mode-check
description: Use when planning impedance, compliance or soft modes on a joint drive, or when a joint stays stiff though the outer controller asked for softness. Decides whether the drive exposes a torque interface or needs an admittance layer.
---

# Drive mode check

1. List the command interfaces the drive or hardware interface exports (position, velocity, effort) and any inner gains it applies in position mode. Mark anything you could not confirm.
2. If a torque (effort) interface exists, impedance control can run directly and `K` is free. Check the loop rate before choosing large `K` (see the latency budget lesson).
3. If only position exists, felt stiffness is capped near the inner `kp_in`. Compliance needs an admittance layer outside, which needs a measured external torque or joint torque sensor. Without one, say that softness is not available.
4. Deflection under a push `tau_ext`: torque mode `tau_ext/K`, position mode `tau_ext/kp_in`, admittance `tau_ext*(1/K + 1/kp_in)`.

Return the verdict (direct impedance, admittance, or not possible) with the interface evidence. Never switch a real drive's mode.
