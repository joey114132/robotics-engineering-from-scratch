---
name: foot-placement-check
description: Use when writing or reviewing a legged-robot step controller that chooses foot positions to reach a speed, or when walking speed drifts, runs away or oscillates from step to step. Checks the deadbeat rule, step-length scaling and reach limits.
---

# Foot-placement check

1. Write the stance model (`Tc`, step time `T`) and the touchdown state. Confirm the foot rule solves the end-of-stance speed for the foot, not a hand-tuned gain on speed error.
2. Compute the steady step length `2*Tc*v*tanh(T/(2*Tc))` for the target speed and compare it with the commanded step. A step 40% short pumps speed up each step. A step 1.5 times too long makes the speed swing and reverse.
3. Replay any scaling of the deadbeat step length (`step_scale`). A scale below 1 can make the speed run away and a scale above 1 can make it swing or reverse, so check convergence to the requested speed instead of judging by the scale alone.
4. Check clamps. When the reach limit cuts the step below the steady length, the target speed is not reachable. Report that instead of letting speed drift.
5. Check that the foot is chosen from the state at touchdown, including state delay.

Return the steady step length, the commanded step, the sign of the speed trend and any clamp that is active. Never send commands.
