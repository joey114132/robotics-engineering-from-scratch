---
name: sim-gap-ranking
description: Use when a trajectory works in simulation but the real joint lags, undershoots or stops short, or before choosing which physical effect to add to a simulator first. Ranks missing effects by measured divergence.
---

# Sim gap ranking

1. Record one list of open-loop commands (no feedback) and replay it on the real joint and on the sim. Keep the same start state.
2. Plot the angle error over time and compute its RMS. Error growth alone does not tell dynamics, calibration and sensor delay apart, so compare controlled model changes (step 3) before naming a cause.
3. Remove one effect at a time from the real-like model (friction, motor lag, sensor delay, others you suspect) and replay. Rank by RMS error.
4. Release a frictionless, lag-free joint from a nonzero angle with zero command. Check that its relative energy drift stays tiny; if not, fix the integrator before blaming a missing effect.
5. Say that the ranking holds only for these parameters and commands. Repeat it for faster commands before trusting it.

Return the ranked table, the error-over-time plot and the one effect to model first. Never retune gains to hide the gap.
