---
name: rrt-path-check
description: Use when reviewing or tuning a sampling-based planner (RRT and relatives) or its output path before the path is time-parameterised and sent to a controller. Checks determinism, edge validity and post-processing.
---

# RRT path check

1. Confirm the run is reproducible: the seed is fixed and logged, and the same seed gives the same tree.
2. Re-check every tree edge and every path segment with the planner's own collision checker at the same resolution. A path that was never re-checked after post-processing is not validated.
3. Compare the step size with the thinnest obstacle and the checker's resolution. A step longer than the obstacle width needs a swept check, not an endpoint test.
4. Report failure honestly: a run that exhausts its iteration budget returns "no path", with node count and budget, never a straight line.
5. Measure path length before and after shortcutting. The result must be at least the straight-line distance and no longer than the raw path.
6. Remember that a shortcut path has corners. It still needs smoothing and a time parameterisation before a joint can follow it.

Return seed, node count, raw and shortcut lengths, edges rechecked, and pass or fail per item. Never relax the obstacles to make a plan succeed.
