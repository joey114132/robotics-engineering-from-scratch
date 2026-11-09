---
name: force-control-check
description: Use when a robot must press, wipe, insert or follow a surface with a target force, or when contact force is wrong after changing the surface or tool. Checks which axes are force-controlled and whether the gains are stable.
---

# Force control check

1. List the task axes. Mark each as position-controlled or force-controlled. An axis in contact with a surface gets a force law, an axis along the surface gets a position law, and no axis gets both.
2. Flag any contact axis that commands a depth computed from an assumed stiffness. Its force error is the stiffness error times the depth, so ask for a force loop or a measured force.
3. For an integral force loop on a spring surface, check `ke * ki * dt < 2` using the stiffest surface the tool may meet. Leave margin, and add sensor delay and filter lag before trusting the limit.
4. Check first contact. The approach speed must be capped, and the force law should not overshoot at contact.
5. Check the measured force against the target on at least two surfaces of different stiffness.

Return per axis: law, gain, stability margin, and the force error measured on each surface. Never change gains.
