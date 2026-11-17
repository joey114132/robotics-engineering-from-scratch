# Grid Search: Dijkstra to A*

> Learn how a robot finds the shortest route on a map without checking every square.

**Type:** Build   **Prerequisites:** 09/03 Collision Checking   **Time:** ~15 minutes

## In Plain Words

A rover seeks the shortest walk to a flag across a walled grid. Dijkstra expands cells in order of the steps already spent reaching them. A* (A-star) adds a guess of the steps still needed, so cells toward the flag come sooner.

A guess that never exceeds the true steps keeps the shortest walk available. An exaggerated guess can rush into a near gap that leads to a longer walk.

## Key Terms

- **Dijkstra**: a search that expands cells in order of the cost already spent reaching them.
- **A-star**: Dijkstra plus a guess of the cost still to go, so it heads toward the goal.
- **Expanding a cell**: checking that cell's neighbours and adding them to the search.
- **Heuristic (`h`)**: the guess of the remaining cost to the goal.
- **Admissible**: a heuristic that never guesses more than the true remaining cost.
- **Manhattan distance**: cells across plus cells down, ignoring walls.

## The Problem

Picture a delivery robot crossing a grid map. Swap the search method and the route changes by 10 steps, or the run takes ten times as many steps. Writing the search yourself shows why.

## The Concept

A real robot must plan fast and well, and the guess is the knob that trades one for the other.

Dijkstra explores squares in order of how cheap they were to reach, so it spreads everywhere. A* (A-star) adds a guess of how far is left, so it leans toward the goal.

![Priority](../assets/diagram-astar-priority.png)

*Same loop, one extra term.*

If the guess is never too big, A* still finds the best route and skips many squares. If it exaggerates, it rushes toward the goal but may take a longer way.

![Promise](../assets/diagram-astar-promise.png)

*A guess that never exaggerates keeps the best route.*

![Expansions](../assets/fig-astar-expansions.png)

*A bigger weight expands fewer squares but costs more.*

On the trap map a top gap dead-ends, and the exaggerating search dives into it.

![Two rovers](../assets/clip-example.mp4)

*Blue exaggerates and walks farther, so green wins.*

<details><summary>The math (optional)</summary>

Dijkstra expands cells in order of `g`, the cost from the start. A* uses `f = g + w * h`, where `w` scales the guess `h`: `w = 0` is Dijkstra, `w = 1` is A*, `w > 1` exaggerates. With up, down, left and right moves the Manhattan distance (cells across plus cells down) never overestimates, so A* returns Dijkstra's cost; a move changes it by at most 1 while `g` grows by 1, so `f` never falls. With `w > 1` the path costs at most `w` times the best. Trap map: `w = 1` expands 115 cells and finds the 26-step low walk; `w = 4` dives into the top gap and reaches the flag after 95 cells with a 36-step walk (cost jumps from 26 to 36 between weights 2 and 3). On the demo's random 40 by 40 map, Dijkstra expands 1202 cells and A* 152 for the same cost 78.

</details>

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

The only difference between the two searches is the priority given to each square.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/05-grid-search-dijkstra-to-astar -q
python3 phases/09-motion-planning/05-grid-search-dijkstra-to-astar/code/main.py
```

## Use It

Run one grid with the guess off and on, and compare the cost and the squares expanded.

Sources: A* search algorithm, Wikipedia, https://en.wikipedia.org/wiki/A*_search_algorithm (opened 2026-11-10).

## Ship It

`outputs/skill-grid-search-check.md` audits a planner's heuristic, weight and expansion count.

## Exercises

1. Turn the guess off and on and compare how many squares are expanded.
2. Make the guess bigger and watch the route get longer.
3. Allow diagonal moves and think about which guess is still safe.
