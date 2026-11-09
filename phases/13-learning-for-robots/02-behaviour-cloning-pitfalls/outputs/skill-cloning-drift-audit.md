---
name: cloning-drift-audit
description: Use when a behaviour-cloned or imitation policy works on logged data but drifts or fails when it drives. Finds compounding error and chooses a recovery-data fix.
---

# Cloning drift audit

1. Run the policy in simulation or on a safe rig with realistic execution noise. Log per step: action error against the expert (or a reference controller) and distance to the nearest training state.
2. If error is flat and small, the problem is elsewhere. If it rises after the first steps and distance to the data rises first, it is compounding error.
3. Fix by adding data from the learner's own states: DAgger-style labelling by the expert or a planner, or deliberate off-path demonstrations. Check the error curve and the success rate after each round.
4. Do not call it fixed from held-out demonstration loss. Report rollout error and success rate.

Return the error-over-horizon curve, the step where distance to data jumps, and the rounds needed. Never run a rollout on shared hardware without approval.
