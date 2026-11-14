# Consensus

> Robots that only talk to neighbours can still agree on one number, and how fast they agree is set by the second-smallest eigenvalue of the graph Laplacian.

**Type:** Build   **Prerequisites:** eigenvalues of a symmetric matrix   **Time:** ~15 minutes

## In Plain Words

Eight toy cars each point a different way and see only their neighbours. Every tick, a car turns a little toward the headings it sees. Two cars pull on each other equally, so whatever one gains the other loses, and the average heading never changes.

Connected cars settle on that starting average. Separate groups settle on different headings. A turn that is too big overshoots the neighbour's heading by more than the original gap, so the difference grows.

## The Problem

Eight robots each measure the same quantity with a different error, and none can hear all the others. With messages only to radio neighbours, every robot should end up at the group average. Some layouts agree fast, some crawl, and a split fleet never agrees.

## The Concept

![Update](../assets/diagram-consensus-update.png)

*Each robot steps a little toward its neighbours' average every tick.*

![Modes decay](../assets/diagram-consensus-modes.png)

*Disagreement splits into modes that each shrink at their own speed. Fast ones vanish, the slowest sets the pace, and a zero eigenvalue never decays.*

![Three graphs](../assets/fig-consensus-states.png)

*The ring crawls to the average, the complete graph needs about ten ticks, and two disconnected groups settle on different values.*

![Decay rate](../assets/fig-rate-vs-lambda2.png)

*Ring, complete, path and star graphs all fall on y = x, so the measured decay rate is eps times lambda2.*

Let `x_i` be car `i`'s heading. One tick moves every car by `eps * sum_j (x_j - x_i)` over its neighbours `j`, with `eps` a small step size. For all cars at once, `x <- (I - eps L) x`, where `I` is the identity matrix and `L = D - A` the graph Laplacian (`A` marks neighbours, `D` counts them). `L` is symmetric and its rows sum to zero, so the all-ones vector has eigenvalue 0 and the average never changes. Every other eigenvector `v_k` (a mode, an independent pattern of disagreement) shrinks by `1 - eps * lambda_k` each tick.

With `eps = 0.05` on a ring, the car at x = 7 sees neighbours 2 and 0, so one tick gives 7 + 0.05 * ((2 - 7) + (0 - 7)) = 6.4.

![Car clip](../assets/clip-example.mp4)

*Green car at x = 7 (1 unit drawn as 0.25 rad; grey arrow = first heading). The first tick, slowed to 0.8 s, turns it about 9 degrees; 19 more play fast.*

The error is stable when `eps * lambda_max < 2`. When `eps` is small enough that no factor goes negative, the slowest decay is `1 - eps * lambda2`.

## Build It

`laplacian()` builds `D - A`, `lambda2()` takes the second eigenvalue, `run()` iterates the update.

```python
M = np.eye(len(A)) - eps * laplacian(A)
out.append(M @ out[-1])
```

Tests check the average is preserved, the per-tick contraction equals `1 - eps * lambda2`, and a step size above `2 / lambda_max` diverges.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/14-multi-robot-and-swarms/02-consensus -q
python3 phases/14-multi-robot-and-swarms/02-consensus/code/figure.py
```

## Use It

Cross-check `lambda2` with `numpy.linalg.eigvalsh` on a graph from your own radio logs. Sources: Wikipedia, Algebraic connectivity (opened 2026-11-09): "This eigenvalue is greater than 0 if and only if G is a connected graph."

## Ship It

`outputs/skill-consensus.md` checks a communication graph and step size before a fleet runs consensus.

## Exercises

1. Add one long-range link to the ring and measure how much `lambda2` and the tick count change.
2. Drop each edge with probability 0.2 every tick and plot the mean ticks to agree.
3. Fix robot 0's value and show everyone converges to it.
