---
name: occupancy-grid-check
description: Use when an occupancy grid or SLAM map shows doubled, slanted or thick walls, ghost rooms, or when building a log-odds grid from range scans. Separates a mapping bug from a pose error.
---

# Occupancy grid check

1. Replay the same scans with the true or best-known poses. If the walls become sharp, the fault is the poses, not the grid code.
2. If walls stay thick with good poses, check the update: one update per cell per scan, end cell raised, crossed cells lowered, log-odds clamped, and the beam range noise smaller than a cell.
3. Doubled walls after a loop can come from accumulating heading error. Check the track width and the gyro or wheel scale before blaming the mapper.
4. Report the share of occupied cells that match a reference, the accumulated heading error over the loop, and which step of the replay fixed the map.

Never edit thresholds to hide a smeared map.
