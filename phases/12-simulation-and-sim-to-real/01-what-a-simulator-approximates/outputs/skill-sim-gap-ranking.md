---
name: sim-gap-ranking
description: Use when a trajectory works in simulation but the real joint lags, undershoots or stops short, or before choosing which physical effect to add to a simulator first. Ranks missing effects by measured divergence.
---

# Sim gap ranking

1. Record one list of open-loop commands (no feedback) and replay it on the real joint and on the sim. Keep the same start state.
2. Compute the angle error over time and its RMS. If it grows with time, the gap is dynamics. If it is a constant shift, suspect calibration or sensor delay.
3. Remove one effect at a time from the real-like model (friction, motor lag, sensor delay, others you suspect) and replay. Rank by RMS error.
4. Check that a frictionless, lag-free run conserves energy. If not, fix the integrator before blaming a missing effect.
5. Say that the ranking holds only for these parameters and commands. Repeat it for faster commands before trusting it.

Return the ranked table, the error-over-time plot and the one effect to model first. Never retune gains to hide the gap.
