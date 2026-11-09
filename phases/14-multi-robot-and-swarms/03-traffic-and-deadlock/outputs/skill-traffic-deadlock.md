---
name: traffic-deadlock
description: Use when reviewing or designing a traffic rule for several robots sharing single-lane cells, corridors or intersections, or when a fleet stops with robots waiting on each other. Finds wait-for loops and checks that the rule cannot create one.
---

# Traffic deadlock check

1. List the shared resources (cells, corridor segments, doors) and their capacity. Capacity 1 is where loops form.
2. Build the wait-for graph: robot A to robot B when B occupies or holds what A needs next. Look for a cycle, including a length-2 head-on swap.
3. Name which of the four conditions the rule breaks: exclusive use, hold-and-wait, no preemption, circular wait. If none, the rule can deadlock.
4. Test in simulation on random jobs with many robots. Count finished jobs per tick and the number of ticks with no progress.
5. Report the throughput cost of the fix (whole-route reservation levels off at lower throughput).

Return the cycle found (robots and cells), the condition broken by the fix and throughput before and after. Never test on real robots or a shared floor before the simulation shows no frozen run.
