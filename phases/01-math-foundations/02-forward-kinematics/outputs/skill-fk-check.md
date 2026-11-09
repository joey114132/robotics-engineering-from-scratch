---
name: fk-check
description: Use when writing or reviewing forward-kinematics code or a URDF-derived chain. Cross-checks against an independent formulation and the reach bounds.
---

# FK cross-check

1. Implement or find a second formulation (planar cumulative angles, or a library chain). Compare on at least 20 random joint vectors to 1e-9.
2. For every pose, assert `lo <= |tip| <= hi` using `reach_bounds`. A violation means the link lengths or units are wrong.
3. Check the zero pose by hand against the drawing: straight, folded, or bent.
4. State the unit of every angle (rad) and length (m) at each interface. Degrees entering a `cos` is the usual silent failure.
5. List which frame each URDF `<origin>` is expressed in.

Return PASS or `file:line` failures. Never edit.
