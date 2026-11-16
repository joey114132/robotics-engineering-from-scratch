# Policy Gradients

> Learn how a robot can improve from points alone, with no teacher, and why the learning wobbles.

**Type:** Build   **Prerequisites:** 13/01 Imitation from Demonstrations   **Time:** ~15 minutes

## In Plain Words

A toy car must stop on a line, and nobody tells it how. Each try earns points, more when it ends nearer the line. You change its steering rule so moves from high-scoring tries become more likely.

A flat bonus on every try lifts every move and hides small differences. Subtract the other tries' average and better moves rise while worse ones fall.

## Key Terms

- **Reward-to-go**: the rewards from the current step to the end of the episode.
- **Return**: the total reward of one episode.
- **Episode**: one try from start to finish.
- **Policy gradient**: nudging the policy's numbers toward actions that earned above-average return.
- **Baseline**: an average subtracted from the return to calm the estimate.
- **Variance**: how much an estimate jumps around between runs.

## The Problem

A toy car must stop on a line and nobody can show it how. You can only score each try. Random tries score wildly, so two training runs with the same settings can look very different.

## The Concept

When no expert exists, trial and error with a score is the only teacher a robot has.

![REINFORCE loop](../assets/diagram-reinforce-loop.png)

*Sample actions, add up rewards, weight each nudge by its return, then change `w` and `b`.*

The policy is a Gaussian (a bell-shaped random choice): the car steers near `w*x + b` plus exploration noise. Multiplying each action's nudge direction (`score()`) by the return and averaging estimates the gradient of expected return.

![Baseline](../assets/diagram-baseline-effect.png)

*When every return is large, every action is pushed up and the signal hides. The baseline cuts this spread.*

![Curves](../assets/fig-reinforce-baseline.png)

*Left: the baseline climbs steadily, raw wobbles (ten seeds, ten repeats with other random draws). Right: the baseline cuts the spread to a third.*

Four tries from one start return 35.93, 34.91, 27.63 and 27.26. As is, all four are pushed up, the best only 32% harder than the worst. With the baseline the pushes become +6.0, +4.6, -5.1 and -5.6.

![Cars with arrows](../assets/clip-example.mp4)

*Blue arrows are almost equal. Then each shows its difference from the others' average, drawn 4 times longer.*

## Build It

The task is a 1-D reach: steering `a` moves the car from `x` to `x' = x + 0.2*a`, and each step pays `3 - x'^2 - 0.01*a^2`. Episode `i`'s baseline is the mean reward-to-go of the other episodes, so it never sees its own action.

```python
G = np.array([reward_to_go(r) for _, _, r in eps])
b = (G.sum(0) - G) / (batch - 1) if baseline else np.zeros_like(G)
g += sum(score(theta, x, a) * (G[i, t] - b[i, t]) for t, (x, a) in enumerate(zip(xs, acts)))
```

Tests check `score()` against a finite difference.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/03-policy-gradients -q
python3 phases/13-learning-for-robots/03-policy-gradients/code/figure.py
```

## Use It

Compare gradient variance across seeds first.

Sources: OpenAI Spinning Up, "Intro to Policy Optimization", opened 2026-11-09.

## Ship It

`outputs/skill-policy-gradient-debug.md` lists what to measure when a run is unstable.

## Exercises

1. Try `BONUS` 0 and 10.
2. Make `SIGMA` learnable and derive its score term.
3. Use the all-episode mean as baseline. Is it biased at `batch=2`?
