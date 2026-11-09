---
name: nav-drift-triage
description: Use when a mobile robot in simulation or on a bench misses its goal, hits a wall, or follows a path that looked fine in the planner. Separates a bad plan from a drifting pose estimate and names the next check.
---

# Navigation drift triage

1. Log three poses over time: the planned path, the robot's estimate and the true pose (from the simulator or an external reference).
2. Estimate follows the path but truth does not: the pose estimate is the problem. Plot `|truth - estimate|` over time. A steady climb means odometry bias, scale error or a wrong wheel radius or track width.
3. Truth and estimate agree but the robot leaves the path: tuning problem. Check lookahead distance and turn-rate limits.
4. Path itself touches an inflated cell: planner problem. Check the inflation radius against the robot radius and the corner-cutting rule.
5. If a landmark fix exists, check the fix interval against the drift rate, and that the fix is only applied when two landmarks are in view.
6. Return the failing stage, the number that shows it and one next check. Never retune gains or change the map without saying so.
