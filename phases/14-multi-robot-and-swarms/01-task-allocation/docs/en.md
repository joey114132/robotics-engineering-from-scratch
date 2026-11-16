# Task Allocation

> Learn how to hand out jobs to a team of robots so the total travel is smallest.

**Type:** Build   **Prerequisites:** 08/01 Differential Drive and Odometry   **Time:** ~15 minutes

## In Plain Words

Five toy cars each need a different pad. If every car takes the nearest free pad in turn, the last car may be left with a pad across the floor.

Task allocation compares every car-to-pad distance. The Hungarian method may revise earlier matches to find the smallest total.

## Key Terms

- **Task allocation**: deciding which robot does which task.
- **Greedy**: choosing the best-looking option at each step without looking ahead.
- **Assignment**: a one-to-one pairing of robots to tasks.
- **Cost matrix `C`**: a table of the distance from each robot to each task.
- **Hungarian method**: an algorithm that finds the assignment with the lowest total cost.
- **Augmenting path**: a chain of swaps that rearranges matches to fit one more pair.

## The Problem

A warehouse has ten robots and ten pick-up points. If each robot grabs the closest free point in turn, the last one may cross the whole floor.

## The Concept

Handing out jobs one by one wastes battery and time, so robots must plan as a group.

![Greedy trap](../assets/diagram-greedy-trap.png)

*An early cheap pick forces a later costly one: car 4 takes the only pad near car 5.*

![Optimal idea](../assets/diagram-optimal-idea.png)

*The Hungarian method prices rows and columns, then flips matches along augmenting paths until the total is minimal.*

![Assignment map](../assets/fig-assignment-map.png)

*Greedy crosses the map; optimal pairs stay local.*

![Cost gap](../assets/fig-cost-gap.png)

*Greedy costs about 1.12 times the optimum at N = 4 and 1.28 times at N = 32 (300 layouts each).*

`C[i, j]` is the distance from robot `i` to task `j`. Find the smallest total.

In the clip, cars 1 and 2 take the same pads either way (1.29 m). Cars 3 to 5 decide the rest (metres):

| car \ pad | 1 | 3 | 5 |
|---|---|---|---|
| 3 | 0.65 | 0.69 | 1.53 |
| 4 | 0.52 | 1.43 | 1.14 |
| 5 | 2.36 | 2.22 | 0.77 |

Greedy: 0.65 + 1.14 + 2.22 = 4.01 m. Best: 0.69 + 0.52 + 0.77 = 1.98 m. With cars 1 and 2 the totals are 5.3 m and 3.3 m.

![Five cars](../assets/clip-example.mp4)

*Blue (`greedy()`): car 5 crosses the floor. Green (`hungarian()`): cars 3, 4, 5 trade pads.*

## Build It

`greedy()` takes the cheapest free task for each robot. `hungarian()` keeps prices `u`, `v` on rows and columns until each robot is matched.

```python
cur = C[i0 - 1, j - 1] - u[i0] - v[j]   # reduced cost of edge (robot i0, task j)
```

Tests compare it with brute force up to N = 6, then SciPy at N = 30.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/14-multi-robot-and-swarms/01-task-allocation -q
python3 phases/14-multi-robot-and-swarms/01-task-allocation/code/figure.py
```

## Use It

`scipy.optimize.linear_sum_assignment` solves the same problem, and the test checks the totals match.

Sources: SciPy docs, `linear_sum_assignment` (opened 2026-11-09).

## Ship It

`outputs/skill-task-allocation.md` picks an assignment method.

## Exercises

1. Allow more tasks than robots with zero-cost dummy robots.
2. Use grid path length instead of straight-line distance.
3. Make greedy pick the cheapest pair first.
