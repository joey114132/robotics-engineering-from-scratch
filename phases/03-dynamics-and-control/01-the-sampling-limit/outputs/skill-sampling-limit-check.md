---
name: sampling-limit-check
description: Use when a damping or velocity gain (kd) is sent from a host loop to a joint, before the gain reaches hardware. Computes dt*kd/J per joint at the lowest-inertia pose.
---

# Sampling-limit check

For every joint with host-side damping:

1. Take `dt` from the real loop period (measured, not the nominal rate).
2. Take `J` as the lowest effective inertia over the workspace, including an extended elbow for the wrist.
3. Compute `r = dt*kd/J`. `r <= 1` PASS (at `r = 1` velocity is zero after one tick, a deadbeat with no sign flip), `1 < r < 2` chatter (WARN: sign flips every tick but decays), `r >= 2` BLOCK (at 2 it rings forever, above 2 it grows).
4. For a wall or limit spring, require damping in both directions of travel, and clip the wall so it can only push outward.

Return a table `joint, dt, J, kd, r, verdict` and the largest safe `kd = J/dt`. Never edit gain files.
