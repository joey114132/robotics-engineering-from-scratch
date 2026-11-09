---
name: policy-wrapper-audit
description: Use before a learned policy (imitation, RL or planner) drives a joint or actuator, even in simulation. Checks that the code between the model and the command covers range, rate of change and stale observations, and that every rule counts its interventions.
---

# Policy wrapper audit

1. Find the last function the action passes through before the actuator. If the model output reaches the command with no code in between, stop: there is no wrapper.
2. Range: confirm a hard clip to the actuator limit. Test it with an action ten times larger than any seen in training.
3. Rate: confirm a limit on the change per step, and that it also applies to fallback commands, so a hold does not jump.
4. Staleness: confirm the observation carries an age, that a dropped message ages it, and that an age over a stated limit replaces the action with a defined hold command. Say what the hold command is and why it is safe for this joint (gravity needs a holding torque).
5. Counts: confirm each rule counts how often it changed the action and that a clean run reports zero clip and zero hold.
6. Run two injected faults, a one-step spike and a multi-step dropout, with and without the wrapper. Report peak command, peak joint position against its limit, and the counts.
7. Never edit the policy or retrain it. Return a pass or fail per rule with the number that shows it.
