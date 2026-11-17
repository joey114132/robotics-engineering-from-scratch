---
name: point-and-distance-check
description: Use when a program stores positions as numbers, measures a distance between two places, or mixes positions counted from different corners or origins. Checks the origin, the units and the distance recipe.
---

# Point and distance check

1. Say where the origin is and which way each number counts (across, up). Two positions are only comparable if they were counted from the same origin.
2. Say the unit (metres, centimetres, pixels) and keep it the same for every number.
3. Distance between two points: subtract to get the gap on each axis, then take the diagonal with `math.hypot` (or `math.dist`). Do not add the gaps.
4. Test it with a case whose answer you know: across 3 and up 4 must give 5.
5. Move the origin and check that the distances do not change.

Report the origin, the unit and the one known case you tested. Do not trust a distance computed from points that were counted from different origins.
