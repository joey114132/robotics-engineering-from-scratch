---
name: transform-sanity
description: Use when reviewing code that composes, inverts or applies rigid transforms (hand-eye, TF chains, FK). Checks multiplication order, frame naming, inverse form and orthonormality drift.
---

# Transform sanity check

1. Name each transform `T_<to>_<from>`. A product must chain inner names: `T_a_b @ T_b_c`. Flag any product whose inner names differ.
2. Every inverse is `[R^T, -R^T p]` or is followed by an `is_rotation` check. Flag bare `np.linalg.inv` on a pose.
3. After many compositions (filters, long chains) re-orthonormalise `R` and report the drift `max|R^T R - I|`.
4. A point transform is `R x + p`. Flag code that applies only `R` to a position.
5. State the frame of every printed pose. A pose without a frame name is not reviewable.

Return PASS or a list of `file:line` violations. Never edit.
