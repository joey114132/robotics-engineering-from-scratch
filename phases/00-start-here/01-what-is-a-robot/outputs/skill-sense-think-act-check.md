---
name: sense-think-act-check
description: Use when a robot job, behaviour or program is described and must be broken into parts, or when a robot ignores something it should have reacted to. Splits the job into sense, think, act and checks that the loop repeats.
---

# Sense, think, act check

1. Name the sensor reading the robot uses, with its unit (for example "distance to the wall, metres"). If nothing is measured, the robot is following a plan blindly.
2. Write the decision as one rule from the reading to a command (for example "distance above 0.5 m: speed 1.0, otherwise 0").
3. Name what acts (motor, wheel, joint) and what one pass of the loop changes.
4. Check that the loop repeats and that the new reading comes from the world after the move, not from a stored value.
5. Run it with the wall (or target) in a different place. A loop that senses still works. A plan with a fixed time or distance does not.

Report the sensor, the rule, the actuator and the loop time step. Do not add speed, filtering or planning until the plain loop works.
