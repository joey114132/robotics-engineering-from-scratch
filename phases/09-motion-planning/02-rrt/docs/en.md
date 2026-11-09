# RRT

> Grow a tree of short, collision-free steps from the start until a branch touches the goal, then straighten the result.

**Type:** Build   **Prerequisites:** none beyond basic geometry   **Time:** ~15 minutes

## The Problem

The straight line from the start pose to the goal pose passes through an obstacle, so you need a path around it. A hand-drawn detour does not carry over to the next scene. A random planner finds a path quickly, but the first path wanders and the arm would follow every detour.

## The Concept

![One RRT growth step](../assets/diagram-rrt-loop.png)

*Each iteration samples a point, steps from the nearest tree node toward it, and keeps the step only if the segment is free.*

The tree is rooted at the start. A random sample pulls the nearest node toward itself, and the step is capped so the tree grows in small, checkable pieces. About one sample in ten is the goal itself, which biases the tree toward it. When a new node can see the goal, the path is read back through the parent links.

![Tree, path and the shortcut path](../assets/fig-rrt-tree-path.png)

*Left: the tree and the first path found. Right: the same path after shortcutting.*

![Path shortcutting](../assets/diagram-shortcut.png)

*Pick two points on the path. If the straight segment between them is free, drop everything in between.*

![Path length over 20 seeds](../assets/fig-rrt-lengths.png)

*Shortcutting shortens the path for every seed, and none gets below the blocked straight line.*

## Build It

```python
new = buf[i] + d / dist * min(step, dist)
if not seg_free(buf[i], new, obstacles):
    continue
buf[n] = new; parent.append(i); n += 1
```

`seg_free` finds the closest point of the segment to each circle centre, so it catches a segment whose endpoints are both outside. Everything is seeded: the same seed gives the same tree.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/02-rrt -q
python3 phases/09-motion-planning/02-rrt/code/main.py
```

## Use It

Swap the brute-force nearest search for `scipy.spatial.cKDTree` once the tree has thousands of nodes. The last test checks that both return the same node.

Sources: [RRT, Wikipedia](https://en.wikipedia.org/wiki/Rapidly-exploring_random_tree) (opened 2026-11-09: tree rooted at the start, nearest-node connection, growth-factor limit). [CHOMP, Ratliff et al. 2009](https://www.ri.cmu.edu/pub_files/2009/5/icra09-chomp.pdf) (opened 2026-11-09: sampled paths are post-processed to remove jerky motion, and the shortcut heuristic replaces a sub-path with a shorter one).

## Ship It

`outputs/skill-rrt-path-check.md` reviews a sampling-based planner's output before it is time-parameterised.

## Exercises

1. Set `goal_bias` to 0 and to 0.5 and compare node counts over 10 seeds.
2. Replace `seg_free` with an endpoint-only check, make obstacles thinner than `step`, and find a seed where an edge cuts through.
3. Run `shortcut` twice and decide whether a second pass can still help.
