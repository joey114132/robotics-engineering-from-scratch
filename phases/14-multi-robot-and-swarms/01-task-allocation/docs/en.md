# Task Allocation

> Assigning each robot its nearest task one at a time is fast and often wrong. The optimal assignment looks at all pairs at once.

**Type:** Build   **Prerequisites:** 08/01 Differential Drive and Odometry   **Time:** ~15 minutes

## The Problem

Ten robots and ten pick-up points. You let each robot grab the closest free point, and one robot ends up driving across the whole floor because everyone near its point was taken first. The fleet's total travel is larger than it needed to be, and no single decision looked wrong.

## The Concept

![Greedy assignment strands a robot](../assets/diagram-greedy-trap.png)

*Greedy decides robot by robot, so an early cheap pick can force a later expensive one.*

![The idea behind optimal assignment](../assets/diagram-optimal-idea.png)

*The Hungarian method keeps a price per row and column and flips matches along augmenting paths until the total is minimal.*

![Greedy against optimal on one layout](../assets/fig-assignment-map.png)

*Same ten robots and ten tasks. Greedy crosses the map several times. The optimal assignment is almost all short, local pairs.*

![Cost gap over random instances](../assets/fig-cost-gap.png)

*Over 300 random layouts per size, greedy costs about 1.12 times the optimum at N = 4 and about 1.28 times at N = 32. It is never cheaper.*

The cost is `C[i, j]`, the distance from robot `i` to task `j`. We want the permutation that minimises the sum of `C[i, perm[i]]`.

## Build It

`greedy()` loops over robots and takes the cheapest free task. `hungarian()` keeps potentials `u`, `v` and grows an alternating tree until each robot is matched.

```python
cur = C[i0 - 1, j - 1] - u[i0] - v[j]   # reduced cost of edge (robot i0, task j)
```

Tests compare it with brute force over every permutation for N up to 6, then with SciPy for N = 30.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/14-multi-robot-and-swarms/01-task-allocation -q
python3 phases/14-multi-robot-and-swarms/01-task-allocation/code/figure.py
```

## Use It

`scipy.optimize.linear_sum_assignment` solves the same problem and the test checks that our total equals its total. Compare runtime at N = 200.

Sources: SciPy docs, `linear_sum_assignment` (opened 2026-11-09): "find a complete assignment of workers to jobs of minimal cost"; it uses a modified Jonker-Volgenant algorithm.

## Ship It

`outputs/skill-task-allocation.md` is a checklist for choosing and checking an assignment method for a fleet.

## Exercises

1. Allow more tasks than robots by padding the matrix with zero-cost dummy robots.
2. Replace straight-line distance with grid path length and rerun the gap plot.
3. Make greedy pick the globally cheapest pair first and measure the gap again.
