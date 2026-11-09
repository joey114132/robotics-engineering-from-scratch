---
name: timestep-sweep
description: Use when a simulated result (contact bounce, jitter, energy gain, a controller that only works at one step size) might depend on the time step or integrator, or before raising dt for speed.
---

# Time-step sweep

1. Run the task at a tiny `dt` as the reference. Note the integrator (explicit Euler, semi-implicit Euler, RK4, implicit).
2. Sweep `dt` upward on a log scale, at least 6 values. Plot the one number you care about (rebound height, settling time, energy drift) against `dt`.
3. Check energy on a conservative case. Explicit Euler gains energy at every `dt`. Semi-implicit stays bounded while `w*dt < 2`, where `w` is the highest frequency in the model (stiffest contact).
4. Pick a `dt` on the flat part of the curve, with margin. A result that moves by more than your tolerance is an artifact until proven otherwise.
5. Beware a wrong result that looks plausible: a short contact can stop an instability from blowing up, so test several drop heights.

Return the sweep table, the chosen `dt` and the stiffest frequency. Never accept one run at one step size.
