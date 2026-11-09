---
name: bayes-filter-check
description: Use when reviewing or debugging a localizer or state estimator that keeps a belief over positions (histogram, particle or grid), or when a robot's position estimate spreads out or stays flat. Checks that predict and update both exist and are sound.
---

# Bayes filter check

1. Find the predict step. It must blur or widen the belief by the motion noise. A predict that only shifts the mean is dead reckoning with extra steps.
2. Find the update step. It must multiply by a likelihood and renormalise. Flag any update that adds, averages or overwrites the belief instead.
3. Check the order per cycle: predict with the command, then update with the reading taken after the move.
4. Check the likelihood is sharp enough to matter: a hit and miss weight near 0.5 each never removes doubt. Flag `p_hit` of 0 or 1, which makes a single bad reading fatal.
5. Check mass: the belief must sum to 1 after each step. On a corridor with ends, say where the mass that leaves goes.
6. Plot entropy or variance over a run. Rising without bound means no working update. Never recovering after a wrong reading means an over-confident likelihood.

Return PASS or a list of `file:line` violations. Never edit.
