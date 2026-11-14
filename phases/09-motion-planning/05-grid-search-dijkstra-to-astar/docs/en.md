# Grid Search: Dijkstra to A*

> A* is Dijkstra with a promise: a guess of the distance left that is never too big, which lets it skip cells that cannot be on the best path.

**Type:** Build   **Prerequisites:** 09/03 Collision Checking   **Time:** ~15 minutes

## In Plain Words

A rover must find the shortest walk to a flag across a walled grid. Dijkstra expands cells (checks their neighbours) in order of the steps already spent reaching them. A* also adds a guess of the steps still needed, so cells toward the flag are expanded sooner.

A guess that ignores walls and counts only the gaps across and down never promises more steps than needed, so the shortest walk stays available. An exaggerated guess can rush into a near gap that leads to a longer walk.

## The Problem

A planner finds a route across a grid map in a blink, but you do not know how. Swap its search for another and the path changes by 10 steps, or the run takes ten times as many. Without writing the search yourself you cannot tell the algorithm's effect from the setting's.

## The Concept

![Same loop, one extra term in the priority](../assets/diagram-astar-priority.png)

*Both searches repeatedly expand the cell with the smallest priority. Only the priority differs.*

Dijkstra expands cells in order of `g`, the cost from the start. A* uses `f = g + w * h`, where `h` is a guess of the cost to the goal and the weight `w` scales it: `w = 0` is Dijkstra, `w = 1` is A*, `w > 1` exaggerates. On a 4-connected grid (moves go up, down, left or right) the Manhattan distance, cells across plus cells down, never overestimates, so A* returns the same cost as Dijkstra. One move changes it by at most 1 while `g` grows by 1, so `f` never falls along a path and no cell is expanded twice.

![The heuristic's promise](../assets/diagram-astar-promise.png)

*An `h` that never overestimates (admissible) keeps A* optimal. With `w > 1` the guess can be too big, so the path may cost up to `w` times the best.*

![Expansions and the cost of overestimating](../assets/fig-astar-expansions.png)

*Same map, three searches. Weight 4 expands fewer cells but returns a longer path. Cost jumps from 26 to 36 between weight 2 and 3.*

Worked example, the trap map: two walls, both open along the bottom, and the first also has a top gap that dead-ends at the second wall. With `w = 1` the search expands 115 cells and finds the 26-step low walk. With `w = 4` cells near the flag outrank those near the start, so it dives through the top gap and reaches the flag after 95 cells, but the walk is 36 steps.

![Two rovers, two guesses](../assets/clip-example.mp4)

*Watch who arrives first. Blue (`w = 4`) leaves first but walks farther, so green (`w = 1`) wins.*

## Build It

```python
heap = [(w * manhattan(start, goal), 0, start)]
while heap:
    _, _, cell = heapq.heappop(heap)
    if cell in closed:
        continue
    closed.add(cell)
    for n in neighbours(cell):
        if g[cell] + 1 < g.get(n, 1e9):
            g[n] = g[cell] + 1
            heapq.heappush(heap, (g[n] + w * manhattan(n, goal), -g[n], n))
```

On the demo's random 40 by 40 map, Dijkstra expands 1202 cells and A* 152 for the same cost 78.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/05-grid-search-dijkstra-to-astar -q
python3 phases/09-motion-planning/05-grid-search-dijkstra-to-astar/code/main.py
```

## Use It

Run the same grid with `w = 0` and `w = 1` and compare cost and cells expanded.

Sources: A* search algorithm, Wikipedia, https://en.wikipedia.org/wiki/A*_search_algorithm (opened 2026-11-10).

## Ship It

`outputs/skill-grid-search-check.md` audits a planner's heuristic, weight and expansion count.

## Exercises

1. Allow diagonal moves and find a heuristic that stays admissible.
2. Break the tie on `g` the other way and count the extra cells.
3. Find the smallest `w` that makes the trap map return cost 36.
