---
name: singularity-guard
description: Use when a velocity or resolved-rate controller inverts a Jacobian, when joint speeds spike near a straight or folded arm, or when a Cartesian move stalls or jerks. Adds a manipulability monitor and a damped solver.
---

# Singularity guard

1. Compute `manipulability(J)` (or the smallest singular value of `J`) every control step and log it with the pose.
2. Replace the plain inverse with damped least squares. The joint speed norm is then bounded by `|v| / (2 lam)`. Choose `lam` so that bound is below the drive's speed limit.
3. Report the tip velocity error the damping causes next to the speed it saves. A controller that hides the lag is wrong, not safe.
4. Test at poses with `q2` of 0.5, 0.1, 0.02 and 0.005 rad: plain speed must grow about like `1 / q2`, damped speed must stay under its bound.

Return the bound, the worst joint speed and the worst tip error over the tests. Never raise `lam` silently to make a test pass.
