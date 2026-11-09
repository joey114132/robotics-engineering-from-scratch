---
name: pick-place-miss-triage
description: Use when a simulated or real arm pick-and-place misses its place point and you need to know which stage (IK, path, gravity feedforward, gains, dynamics model) caused it. Reads tip error over time and returns the likely stage.
---

# Pick-and-place miss triage

1. Record tip position against the planned tip for the whole run, plus the final error at the place point.
2. Constant offset that holds while the arm rests: gravity residual. Residual torque is about `kp * offset`. Check the feedforward scale first.
3. Error that appears only during motion and returns to zero: tracking lag. Check path duration, `kd`, and whether acceleration feedforward is missing.
4. Error at a waypoint before the arm moves: IK branch or reachability. Check `fk(ik(p))` against `p`.
5. Error that grows or rings: gains too high for the sample time, or a wrong Coriolis term. Run the free-swing energy test.
6. Report the stage, the number that points to it and the next single check. Never change gains.
