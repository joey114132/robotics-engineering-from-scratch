# Pose Graph and Loop Closure

> Treat poses as unknowns and measurements as springs between them, and one late "we are back here" measurement bends the whole drifted trajectory shut.

**Type:** Build   **Prerequisites:** 08/05 Scan Matching with ICP, 07/02 Kalman Filter   **Time:** ~15 minutes

## In Plain Words

A rover drives a square, but its wheels err a little each step, so its path ends away from the start. Moving only the last pose leaves every earlier turn misplaced.

A pose graph links each stop to the next with a measured move, like a spring. Recognising the start adds a spring from the end to the start. With the first pose fixed, all poses shift together to stretch every spring as little as possible. Reliable springs pull harder. A false match pulls the map out of shape.

## The Problem

You drive a 5 m square and odometry says the robot ended 1.4 m from the start. A scan match (08/05) says the last scan looks exactly like the first. Overwriting the last pose fixes one point; every earlier pose and the map stay bent.

## The Concept

![Poses and springs](../assets/diagram-posegraph-springs.png)

*Each odometry step is a spring between neighbouring poses. The loop closure is one more spring, last pose to first.*

A pose is `(x, y, heading)`. An edge from pose `i` to `j` carries a measurement `z`, the pose of `j` as seen from `i`. Its residual, how far the spring is stretched, is `between(x_i, x_j) - z`: the current guess of that view minus the measured one, with the heading difference wrapped into one turn. Each residual is divided by its noise, so trusted springs are stiffer. The cost is the sum of squared residuals.

The square's poses 0 to 20 sit one per metre, so 5, 10, 15 and 20 are corners (20 = start). Odometry ends 1.42 m away, with rms error 0.70 m (typical pose distance from the truth). A true closure spreads that gap along the loop: poses 5, 10, 15 and 20 move 0.20, 0.59, 1.03 and 1.41 m, and the rms error falls to 0.09 m. A false closure (the end matched to a place 3 m and 2 m off) raises it to 1.88 m.

![False and true loop closure](../assets/clip-example.mp4)

*Watch the amber spring. Blue (false closure) ends 3.6 m from the start, green (true closure) closes the square.*

![Repair pipeline](../assets/diagram-posegraph-pipeline.png)

*One closure edge enters, then every pose is re-solved.*

Gauss-Newton treats residuals as straight lines and repeats the step that most reduces the cost. Sliding the whole map in x or y, or turning it, changes no residual, so those three directions are undetermined until pose 0 is held fixed.

![Loop before and after closure](../assets/fig-posegraph-loop.png)

*Left: odometry drifts open, and the solved path lands on the square. Right: the error shrinks along the whole loop.*


## Build It

```python
def residuals(X, edges):
    out = []
    for i, j, z, w in edges:
        e = between(X[i], X[j]) - z
        e[2] = wrap(e[2])
        out.append(w * e)
    return np.concatenate(out)

J = jacobian(X, edges, free=range(1, len(X)))   # numeric, pose 0 held fixed
dx = np.linalg.lstsq(J, -residuals(X, edges), rcond=None)[0]
```

Tests check that cost never rises, pose 0 stays put, and a wrong closure worsens the map.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/06-pose-graph-and-loop-closure -q
python3 phases/08-mobile-robots/06-pose-graph-and-loop-closure/code/main.py
```

## Use It

g2o solves SLAM as a graph of poses and constraints by nonlinear least squares (Gauss-Newton or Levenberg-Marquardt). Build this graph there and compare poses with `solve()`.

Sources: Kümmerle et al., g2o: A General Framework for Graph Optimization (ICRA 2011),
http://ais.informatik.uni-freiburg.de/publications/papers/kuemmerle11icra.pdf
(found by search 2026-11-10, abstract-level summary only).

## Ship It

`outputs/skill-pose-graph-check.md` audits a pose-graph solve for a missing anchor, bad edge weights and a false closure.

## Exercises

1. Remove the heading bias; does the closure still help?
2. Make the closure 10 times less certain; watch the error.
3. Add a second closure between poses 5 and 15 and compare.
