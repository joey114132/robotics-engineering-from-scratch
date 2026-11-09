---
name: consensus
description: Use before running average consensus or a distributed averaging step on a robot fleet, or when agreement is slow or never happens. Checks connectivity, step size and expected convergence time from the communication graph.
---

# Consensus check

1. Build the adjacency matrix from who can really hear whom, in both directions. One-way links break the average-preserving property.
2. Compute `L = D - A` and its eigenvalues. If `lambda2` is not above zero (numerically, above 1e-9), the graph is disconnected: say which robots are cut off and stop.
3. Pick `eps` below `2 / lambda_max`. A safe default is `0.4 / max_degree`, because `lambda_max <= 2 * max_degree`.
4. Predict the steps to shrink disagreement by a factor f: about `ln(f) / (eps * lambda2)`.
5. Run it in simulation first and compare the measured per-step contraction with `1 - eps * lambda2`.

Return `lambda2`, `eps`, the predicted and measured steps. Never run it on robots when the graph can change faster than the predicted agreement time without saying so.
