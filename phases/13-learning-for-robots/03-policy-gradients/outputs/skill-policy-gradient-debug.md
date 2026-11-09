---
name: policy-gradient-debug
description: Use when a policy-gradient or REINFORCE-style training run is unstable, seed-sensitive or slow. Measures gradient variance and checks the baseline before touching other settings.
---

# Policy-gradient debug

1. Freeze the policy parameters at the initial values. Compute the gradient estimate 200+ times with fresh episodes, with and without the baseline. Report mean and std per parameter.
2. If the means disagree beyond 4 standard errors, the baseline sees its own sample: build it from other episodes or from a state-only value function.
3. If the spread is large against the mean, look at the return scale: a big constant offset multiplies the noise. Use a baseline or normalise returns before lowering the learning rate.
4. Check the score function against a finite difference of the log probability once.
5. Compare final returns only across 5+ seeds, with min and max, not one curve.

Return per-parameter mean and std for both estimators, and the seed spread of the final return. Never change the reward to make a curve look better without saying so.
