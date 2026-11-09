---
name: pure-pursuit-tuning
description: Use when tuning or debugging a pure pursuit path follower on a differential-drive or similar robot: wobble on straights, cut corners, or a path that is never reached. Picks lookahead from measured wobble and corner cut.
---

# Pure pursuit tuning

1. Replay one logged run and compute two numbers: how many times the robot crosses the path on the first long straight (use a small dead band, about 2 cm), and the closest approach of the trajectory to each corner.
2. Many crossings mean the lookahead is too short for the drive's lag. Raise `Ld`, or lower the speed, and rerun.
3. A large corner cut means `Ld` is too long. Lower `Ld`, or scale it down with speed, or round the corner in the path.
4. If lowering `Ld` brings back wobble, the drive response is the limit. Measure the turn-rate response before tuning further.
5. Report crossings, corner cut and the speed and `Ld` used for each run.

Never change `Ld` for one corner without rechecking the wobble on the straights.
