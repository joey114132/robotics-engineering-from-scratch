---
name: quaternion-sign-check
description: Use when reviewing code that interpolates, averages, filters or compares quaternions (slerp, trajectory blending, orientation targets from a planner or sensor). Checks the double cover, the sign fix and the component order.
---

# Quaternion sign check

1. Find every place two quaternions are interpolated, averaged or differenced. Flag any that does not negate one of them when `dot < 0`.
2. Flag any code that compares quaternions with `==` or a plain distance. Two quaternions are the same rotation if `|dot|` is near 1.
3. State the component order at every library boundary: `(w, x, y, z)` or `(x, y, z, w)`. A mismatch gives a valid unit quaternion for a different rotation.
4. Check that quaternions are normalised after integration and after interpolation, and that matrix conversion uses a branch that stays well conditioned (largest of w, x, y, z).
5. Ask what a 180 degree error does: the path length at that dot value must stay bounded.

Return PASS or a list of `file:line` violations. Never edit.
