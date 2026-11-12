---
name: multimodal-demo-check
description: Use when a cloned or regression-trained policy fails by doing something no demonstration did, such as driving straight at an obstacle that demos pass on either side, or when choosing between mean regression, sampling and action chunking.
---

# Multimodal demo check

1. Group demonstration steps by observation (a nearest-neighbour radius or a clustering). For each group, plot the actions. Two clusters far apart mean the data is multimodal there.
2. Take the mean action of such a group and ask whether anyone ever demonstrated it. If it points at an obstacle or a wall, a mean policy will fail even with zero noise.
3. Run both the mean policy and a sampler that returns a chunk of `H` actions, in simulation, from the ambiguous start. Count collisions over 100 seeds and record action jitter.
4. When chunks overlap, choose each new chunk to agree with the actions already committed. Check that rollouts keep both modes and none blends them.
5. Do not call it fixed from held-out loss. Report collision rate, the share of rollouts per mode and jitter.

Return the ambiguous states, the collision counts and the chunk length used. Never run a sampled policy on shared hardware without approval.
