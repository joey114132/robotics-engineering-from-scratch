---
name: consensus
description: Use before running average consensus or a distributed averaging step on a robot fleet, or when agreement is slow or never happens. Checks connectivity, step size and expected convergence time from the communication graph.
---

# Consensus check

1. Build the adjacency matrix from who can really hear whom, in both directions. One-way links can break the average-preserving property.
2. Compute `L = D - A` and its eigenvalues. If `lambda2` is not above zero (numerically, above 1e-9), the graph is disconnected: say which robots are cut off and stop.
3. Pick `eps` below `2 / lambda_max`. A safe default is `0.4 / max_degree`, because `lambda_max <= 2 * max_degree`.
4. Let `f` be the fraction of disagreement left, with `0 < f < 1`. Compute `rho = max(abs(1 - eps * eigenvalues[1:]))`, the slowest per-step factor over all modes except the average. For `0 < rho < 1`, allow `ceil(log(f) / log(rho))` steps. If `rho == 0`, one update suffices. `1 - eps * lambda2` is only `rho` for a small step.
5. Run the simulation and compare the measured disagreement (the norm of `x` minus its average) with the bound `initial_disagreement * rho**steps`.

Return `lambda2`, `rho`, `eps`, the predicted and measured steps. Never run it on robots when the graph can change faster than the predicted agreement time without saying so.
