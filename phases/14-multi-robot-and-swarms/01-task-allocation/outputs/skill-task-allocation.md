---
name: task-allocation
description: Use when assigning N robots to N tasks by travel cost, or when a fleet's total distance looks higher than it should. Chooses greedy or optimal assignment and checks the result.
---

# Task allocation check

1. Build the cost matrix `C[i, j]` from the metric the robots really pay (path length, not straight line, when walls exist).
2. If N is below about 6, brute force every permutation and use it as ground truth.
3. Run the optimal solver (Hungarian or auction). Run greedy too and report `greedy_total / optimal_total`.
4. Verify the result is a permutation: each task used once. For more tasks than robots, pad with zero-cost dummies.
5. If the ratio is close to 1, greedy is fine and cheaper to maintain. Otherwise ship the optimal one.

Return both totals, the ratio and the assignment. Never reassign robots that already started moving without saying so.
