---
name: jacobian-check
description: Use when a Jacobian is written by hand, copied from a library, or changed, or before using J for resolved-rate control or tau = J^T F. Checks it against finite differences and a power balance.
---

# Jacobian check

1. Build a central finite-difference Jacobian from FK with a step around 1e-6 rad. A step of 1e-12 or 1e-1 gives a wrong reference, so never use those.
2. Compare at 20 or more random poses. The largest entry difference should be below 1e-8 m for a planar arm in float64. A larger gap means a sign, a frame or a link-order bug.
3. Check power: for random `qd` and `F`, `(J^T F) . qd` must equal `F . (J qd)` to rounding.
4. Check units and the reference point: `J` is for one chosen point (the tip, not the wrist), expressed in one frame.

Return the worst entry difference, the pose where it occurs and the power-balance residual. Never edit FK to make a Jacobian pass.
