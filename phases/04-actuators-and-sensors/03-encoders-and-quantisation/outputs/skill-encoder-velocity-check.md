---
name: encoder-velocity-check
description: Use when a joint velocity signal is jumpy at low speed, when choosing a velocity filter or loop rate for an encoder joint, or before raising kd. Computes the velocity step and the noise-versus-delay trade.
---

# Encoder velocity check

1. Get counts per revolution `CPR` (after quadrature decoding), the loop period `dt`, and the typical slowest working speed.
2. Velocity step is `2*pi / (CPR * dt)`. If the slowest working speed is below that step, a one-sample difference is a 0-or-step signal: say so.
3. Window of `n` samples gives step `/n` and delay `n*dt/2` on a changing signal. Pick the smallest `n` whose step is under 10% of the slowest speed, then add the delay to the latency budget.
4. Noise at slow speed is about `step * sqrt(d*(1-d))`, where `d = speed / step`. It is not monotone in `n`: it dips where the window spans whole counts, so do not tune `n` to a dip.

Return the step, the chosen `n`, the added delay and whether `kd` times this velocity will kick the joint. Never change a drive setting.
