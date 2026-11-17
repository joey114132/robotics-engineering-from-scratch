---
name: rotation-check
description: Use when you write or review code that turns a point or a 2D rotation matrix, to check the angle unit, the turn direction and that distances stay the same.
---

# Rotation check

1. Confirm the angle is in radians and that a positive angle turns counter-clockwise.
2. Test a quarter turn: (1, 0) must land on (0, 1) and (0, 1) on (-1, 0).
3. Test that the distance from the origin is the same before and after, for several angles.
4. Test that turning by `a` and then `b` equals turning by `a + b`.
5. If a table (matrix) version exists, check it agrees with the plain formula for a few angles.

Report each failed check with the expected and actual numbers. Do not change code.
