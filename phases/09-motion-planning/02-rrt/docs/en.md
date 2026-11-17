# RRT

> Learn how a robot finds a way around obstacles by trial and error, then straightens the route.

**Type:** Build   **Prerequisites:** none beyond basic geometry   **Time:** ~15 minutes

## In Plain Words

A rover must cross a field with three rocks, so the straight line to the flag is blocked. It picks a random spot, finds the closest point of its route so far, and steps a little toward the spot, keeping the step only if it clears every rock.

RRT repeats this until a branch reaches the flag. The route wanders, so straight shortcuts between its points remove detours.

## Key Terms

- **RRT**: rapidly-exploring random tree, a planner that grows a tree of short steps by random sampling.
- **Node**: one point of the tree; each new node remembers its parent.
- **Goal bias**: the share of samples that are the goal itself, tilting the tree toward it.
- **Shortcutting**: replacing part of a path with a straight segment when that segment is free.
- **Seed**: the starting number of a random generator; the same seed repeats the same run.

## The Problem

Picture a robot arm that must reach a goal past an obstacle. A random planner finds a way round quickly, but the path wanders and the arm would follow every detour.

## The Concept

A real robot cannot hand-draw a detour for every new scene, so it finds one by trying.

Pick a random spot. Find the closest point of the tree grown so far and take one short step toward the spot. Keep the step only if it touches no obstacle. Repeat until a branch reaches the goal.

![RRT step](../assets/diagram-rrt-loop.png)

*Sample, step, keep if free.*

![Two steps](../assets/clip-example.mp4)

*The first step ends inside the rock and is dropped. The second is clear.*

The path found this way wanders. Replace any part of it by a straight shortcut whenever the shortcut is free.

![Tree and path](../assets/fig-rrt-tree-path.png)

*Left: the tree and its first path. Right: after shortcuts.*

![Shortcutting](../assets/diagram-shortcut.png)

*If the straight line is free, drop the points between.*

![Lengths](../assets/fig-rrt-lengths.png)

*Shortcuts shorten every path.*

<details><summary>The math (optional)</summary>

Each sample pulls its nearest node one step of at most `step`; one sample in ten is the goal itself. With `step = 0.4` and a rock at (5, 5) with radius 2, the sample (6.86, 6.5) in iteration 11 pulls node (3.12, 4.07) to (3.46, 4.29), 1.70 from the centre and inside the rock, so `seg_free` fails and the step is dropped. The sample (2.27, 6.23) in iteration 17 pulls the same node to (2.97, 4.44), 2.10 from the centre: kept. `seg_free` uses the closest point of the segment to each circle centre, so it catches segments with both endpoints outside. The first path is 17.96 long and 14.86 after shortcutting. Over 20 seeds shortcutting shortens every path, never below the straight line. One seed gives one tree.

</details>

## Build It

```python
new = buf[i] + d / dist * min(step, dist)
if not seg_free(buf[i], new, obstacles):
    continue
buf[n] = new; parent.append(i); n += 1
```

`seg_free` checks a whole step against every circle. The same seed gives the same tree.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/02-rrt -q
python3 phases/09-motion-planning/02-rrt/code/main.py
```

## Use It

With thousands of nodes, swap the plain nearest search for `scipy.spatial.cKDTree`; a test checks both agree.

Sources: [RRT, Wikipedia](https://en.wikipedia.org/wiki/Rapidly-exploring_random_tree) and [CHOMP, Ratliff et al. 2009](https://www.ri.cmu.edu/pub_files/2009/5/icra09-chomp.pdf), both opened 2026-11-09.

## Ship It

`outputs/skill-rrt-path-check.md` reviews a sampling planner's path.

## Exercises

1. Change how often the goal is sampled and watch the tree.
2. Make an obstacle very thin and see whether a step can cut through it.
3. Run the shortcut step twice and see whether it helps again.
