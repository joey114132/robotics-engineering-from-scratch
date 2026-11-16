# Consensus

> Learn how robots that only talk to their neighbours can still agree on one number, and what makes it slow.

**Type:** Build   **Prerequisites:** eigenvalues of a symmetric matrix   **Time:** ~15 minutes

## In Plain Words

Eight toy cars each point a different way and see only their neighbours. Every tick a car turns a little toward the headings it sees. The average heading never changes.

Connected cars settle on that average. Separate groups settle on different headings. A turn that is too big overshoots.

## Key Terms

- **Consensus**: all robots agreeing on one value by talking only to neighbours.
- **Graph Laplacian `L`**: the matrix `D - A` that encodes who talks to whom.
- **Eigenvalue**: a number saying how fast one pattern in a matrix grows or shrinks.
- **`lambda2`**: the second-smallest eigenvalue of `L`. It sets the agreement speed.
- **Mode**: one independent pattern of disagreement.
- **Step size `eps`**: how far each robot moves toward its neighbours per tick.

## The Problem

Eight robots each measure the same thing with a different error, and each hears only a few nearby robots. They should all reach the group average.

## The Concept

A real fleet has no boss and no radio that reaches everyone, so robots must agree using only local talk.

![Update](../assets/diagram-consensus-update.png)

*Each robot steps a little toward its neighbours' average every tick.*

![Modes decay](../assets/diagram-consensus-modes.png)

*The slowest mode sets the pace. A zero eigenvalue never decays.*

![Three graphs](../assets/fig-consensus-states.png)

*The ring crawls, the complete graph needs about ten ticks, and two split groups disagree.*

![Decay rate](../assets/fig-rate-vs-lambda2.png)

*All four graphs fall on y = x, so the decay rate is eps times lambda2.*

Let `x_i` be car `i`'s heading. One tick moves each car by `eps * sum_j (x_j - x_i)` over its neighbours `j`, or for all cars `x <- (I - eps L) x`. Here `A` marks neighbours and `D` counts them. Rows of `L` sum to zero, so the average never changes. Every other mode shrinks by `1 - eps * lambda_k` each tick.

With `eps = 0.05` on a ring, the car at x = 7 sees neighbours 2 and 0, so one tick gives 7 + 0.05 * ((2 - 7) + (0 - 7)) = 6.4.

![Car clip](../assets/clip-example.mp4)

*Green car at x = 7 (1 unit drawn as 0.25 rad). The first tick turns it about 9 degrees.*

The update is stable when `eps * lambda_max < 2`.

## Build It

`laplacian()` builds `D - A`, `lambda2()` takes the second eigenvalue, `run()` repeats the update.

```python
M = np.eye(len(A)) - eps * laplacian(A)
out.append(M @ out[-1])
```

Tests check the average is preserved, the slowest decay is `1 - eps * lambda2`, and a step above `2 / lambda_max` diverges.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/14-multi-robot-and-swarms/02-consensus -q
python3 phases/14-multi-robot-and-swarms/02-consensus/code/figure.py
```

## Use It

Cross-check `lambda2` with `numpy.linalg.eigvalsh`.

Sources: Wikipedia, Algebraic connectivity (opened 2026-11-09). `lambda2` is above 0 exactly when the graph is connected.

## Ship It

`outputs/skill-consensus.md` checks a graph and step size.

## Exercises

1. Add one long-range link to the ring. What changes?
2. Drop each edge with probability 0.2 per tick.
3. Fix robot 0's value and show everyone converges to it.
