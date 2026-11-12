---
name: ik-solver-check
description: Use when writing or reviewing a numerical inverse-kinematics solver, when an IK call fails near a straight arm or a joint limit, or when the same target gives different joint angles from run to run. Checks damping, limits, restarts and the failure flag.
---

# IK solver check

1. Confirm the step is damped (`J^T (J J^T + lam^2 I)^-1 e`) and the biggest joint step is capped. Test from a straight arm, where `J` loses rank.
2. Confirm every iterate is clamped to the joint limits, and that the result passes `fk(q)` back to the target within the tolerance.
3. Run 20 or more random seeds on one reachable target. Report how many converge and which elbow signs appear.
4. Send an unreachable target and a target blocked by tight limits. The solver must return the lowest-error iterate encountered and `converged=False`, never an exception or a silent `True`. Include the initial and final iterates when choosing it; no global minimum is promised.
5. State how the final solution is chosen among several, for example nearest to the current joint angles.

Return the converged fraction, the signs found, the worst tip error on failures and any missing flag. Never loosen the tolerance to make a seed pass.
