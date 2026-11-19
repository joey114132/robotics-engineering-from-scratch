---
name: policy-safety-wrapper
description: Use when a learned or other non-deterministic policy will drive an actuator, in simulation first, or when reviewing the layer between a policy and the command interface. Checks limits, rate limits, stale-input handling and the intervention log.
---

# Policy safety wrapper review

1. List what the policy can emit: NaN, infinity, values past limits, sudden jumps. For each, find the line in the wrapper that handles it.
2. Check order: usable-observation check, policy call, non-finite replacement, clip, rate limit. The rate limiter must see the fallback too, so a fallback never jumps.
3. Check the stale-input ladder: how many ticks it holds, the deadline and the fallback ramp. With speed `v`, hold time `t_h` (add any delay before braking starts), ramp deceleration `a` and free distance `room`, require `v * t_h + v*v / (2*a) <= room`.
4. Require a fuzz test (thousands of random raw values with NaN and inf) asserting limits and rate on every output, plus a determinism test (same inputs, same output and log).
5. Read the log from a simulated run: counts per kind, first intervention, benign start-up clipping versus real faults.

Return the unhandled outputs, the ladder numbers, and the intervention counts. A high clip rate means retrain or retune the policy, not widen the limits. Never send a command to hardware from this review.
