---
name: collision-step-check
description: Use when a planner or controller checks a path for collisions only at sampled poses or time steps, or when a collision-free path still hits something thin. Compares the check spacing with the thinnest obstacle and picks exact, padded or denser checking.
---

# Collision step check

1. Find the spacing `s` between checked poses along the path in the space where the obstacle lives (metres, not joint radians).
2. Find the thinnest obstacle width `w`. If `s` is greater than `w`, the check can tunnel through it.
3. Prefer an exact segment-versus-shape test. If only sampling is available, grow every obstacle by `s/2` so no real hit is missed, and report the false-alarm cost.
4. For an arm, convert joint-space step to the largest link-point displacement: it is the worst-case spacing, not the joint step.
5. Test the checker on a deliberately thin obstacle placed halfway between two samples. It must report a hit.

Return `s`, `w`, whether tunnelling is possible, the padding used, and a pass or fail on the thin-obstacle test. Never shrink an obstacle to make a path pass.
