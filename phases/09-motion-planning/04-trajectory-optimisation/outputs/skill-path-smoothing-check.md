---
name: path-smoothing-check
description: Use when smoothing or optimising a waypoint path with a smoothness cost and obstacle penalty (CHOMP-like), or when reviewing the result before time-parameterising it. Checks endpoints, clearance, segment validity and step size.
---

# Path smoothing check

1. Confirm the two endpoints are bit-identical before and after. Optimisation must not change the task.
2. Compute clearance at every waypoint and also along every segment with an exact segment test. A penalty on waypoints alone does not protect the segments between them.
3. Verify the analytic gradient against finite differences on one random path before trusting any run.
4. Log total cost per iteration. It must fall every iteration. If it rises, the step size is too large for the cost curvature: lower it, do not add iterations.
5. Check which margin the penalty used and that the final clearance is positive, not just that the cost is small.
6. Remember a soft penalty can leave a path inside the margin. If a hard clearance is required, test it explicitly.

Return endpoint check, minimum waypoint clearance, minimum segment clearance, cost at iteration 1 and last, and pass or fail per item. Never lower the margin or the obstacle radius to make a path pass.
