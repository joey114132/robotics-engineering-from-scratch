---
name: ik-answer-check
description: Use when an inverse-kinematics result (analytic or numerical) is about to be sent to a controller or a simulator, or when IK returns nan or a surprising elbow. Verifies reach, branch and the FK round trip.
---

# IK answer check

1. Compute the target distance `r` from the base. If `r > L1 + L2` or `r < |L1 - L2|`, the target is unreachable: report it and stop. Never clip silently.
2. Name the branch (elbow-up has `q2 < 0`, elbow-down has `q2 >= 0` in the lesson's convention) and check it against joint limits and obstacles.
3. Run FK on the returned angles. The tip must match the target within 1e-6 m for an analytic solver. If not, the solver is wrong, not the target.
4. Near `r = L1 + L2` the two branches merge and joint speeds grow: warn that the answer is close to a singularity.

Return the branch, the FK error and a reach verdict. Never replace an unreachable target with the nearest reachable one without saying so.
