---
name: particle-filter-check
description: Use when writing or reviewing a particle filter for robot localisation, or when a localiser snaps to a wrong pose, never recovers after a bump, or jitters. Checks weights, resampling, noise and kidnap handling.
---

# Particle filter check

1. Weights: are they computed in log form with the maximum subtracted before `exp`? Is there a guard when all weights are zero?
2. Resampling: is the cloud size fixed, and is the resampling low-variance (systematic)? Resampling every step with few particles loses diversity.
3. Motion noise: is it larger than the real motion error? A cloud tuned too tight follows its own drift. Print the particle spread over time.
4. Kidnap and bumps: does the filter keep a small fraction of random particles, or have another recovery path? Replay a run where the true pose jumps and check the error comes back.
5. Report the particle count, the spread, `n_eff`, and the error after a jump.

Never change noise values without a replay that shows both normal and jump runs.
