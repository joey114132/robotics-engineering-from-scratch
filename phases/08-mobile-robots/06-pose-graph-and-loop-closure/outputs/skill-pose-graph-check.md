---
name: pose-graph-check
description: Use when a SLAM or mapping result bends after a loop closure, when adding loop closures to a pose graph, or when a graph solve gives an oddly shifted map. Checks the anchor, weights and the closure itself.
---

# Pose-graph check

1. Confirm one pose (or a prior edge) is held fixed. Without it the Jacobian has 3 free directions (shift x, shift y, rotate) and the solver result is arbitrary.
2. Print every edge's noise and the residual before and after the solve. A closure that moves poses far more than its stated noise allows is suspect.
3. Wrap every heading difference. A residual near 2 pi is a missing wrap.
4. Check each closure against a second source (a second scan match, GPS, or a look at the map). A wrong closure bends the map worse than none.
5. Confirm cost never rises between iterations and that the solve stops on a small step, not on the iteration cap.

Return the anchor, the largest residuals, the closures that need a second check and the cost trace. Never add a closure only to make the loop look shut.
