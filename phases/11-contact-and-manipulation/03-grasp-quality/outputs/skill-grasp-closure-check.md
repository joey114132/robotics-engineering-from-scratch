---
name: grasp-closure-check
description: Use when planning or debugging a grasp, a fixture or a pinch where an object twists, slips or rotates out although the grip force looks sufficient. Tests force closure and the quality margin from contact positions, normals and friction.
---

# Grasp closure check

1. List each contact: position, inward normal, friction coefficient. State the coordinate frame once.
2. Build the two cone-edge wrenches per contact in the plane (force plus torque divided by a stated length). Check the wrench set has rank 3 first; otherwise the grasp cannot close.
3. Test whether the origin is strictly inside the convex hull of the wrenches. Report the distance epsilon, and the length scale it depends on.
4. For two contacts, cross-check by asking whether the line joining them lies inside both friction cones.
5. A closed grasp with a tiny epsilon is fragile: a small error in `mu` or in a normal opens it. Report which contact limits it.

Return CLOSED or OPEN, epsilon, the limiting contact, and the smallest friction that would close it. Never change the grasp.
