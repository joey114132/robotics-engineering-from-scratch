---
name: grid-search-check
description: Use when a grid or graph planner returns a longer path than expected, expands too many cells, or when choosing a heuristic or weight for Dijkstra or A*. Checks admissibility, weight and expansion counts.
---

# Grid-search check

1. Read the heuristic and its weight. `h = 0` is Dijkstra; `w > 1` on an admissible `h` can return a path up to `w` times the best.
2. Confirm the heuristic never exceeds the true cost for the move set in use (Manhattan for 4-connected; not for diagonal moves).
3. Run the same query with `w = 0` and `w = 1`. Costs must match; if A* is longer, the heuristic overestimates.
4. Compare cells expanded. An open map should show a large gap, a maze a small one. No gap points to a poor heuristic or a very high weight.
5. Check no cell is expanded twice. A repeat means an inconsistent heuristic or a missing closed set.

Return the weight, a cost match or mismatch against `w = 0`, the expansion counts and any admissibility violation. Never raise `w` to hide a slow search without reporting the path-cost bound.
