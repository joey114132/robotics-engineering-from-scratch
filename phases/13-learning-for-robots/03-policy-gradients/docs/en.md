# Policy Gradients

> Nudge the policy toward actions that scored above average. The price is an estimate that jumps around, which a baseline calms.

**Type:** Build   **Prerequisites:** 13/01 Imitation from Demonstrations   **Time:** ~15 minutes

## In Plain Words

A toy car has to stop on a line, and nobody tells it how. You only give each try points, more when it ends nearer the line. You then change its steering rule so moves from higher-point tries become more likely.

Suppose every try earns a big flat bonus. Pushing each move up by its whole point total lifts every move, and small differences hide in the bonus. Subtract the average points of the other tries and better moves rise while worse ones fall.

## The Problem

Sometimes there is no expert, only a reward. You try random actions and move toward what worked. The return (total reward) of one episode, one try from start to finish, jumps around, so two training runs with the same settings can look very different.

## The Concept

![REINFORCE loop](../assets/diagram-reinforce-loop.png)

*Follow the numbers. Sample actions, add up the rewards, weight each action's nudge direction by that return, then change `w` and `b`.*

The policy is a Gaussian (a bell-shaped random choice): at position `x` the car steers near `w*x + b`, plus small random exploration noise. `w` and `b` are the two numbers learning changes. Each action has a nudge direction (`score()` in the code), the gradient of its log probability: it says which way to turn `w` and `b` to make that action likelier. Multiply it by the return and average over episodes to estimate the gradient of expected return.

![What a baseline changes](../assets/diagram-baseline-effect.png)

*When every return is large and positive, every action is pushed up and the signal hides in the differences. The baseline cuts this spread, not the exploration noise.*

![Learning curves and gradient spread](../assets/fig-reinforce-baseline.png)

*Left: ten seeds (repeats with other random draws) each; the baseline climbs steadily, raw (no baseline) wobbles. Right: both estimators start with the same mean, and the baseline cuts the spread, how far the estimate jumps, to a third.*

Four tries from one start (`episode()`, seed 2) return 35.93, 34.91, 27.63 and 27.26. As is, all four are pushed up, the best only 32% harder than the worst. With the baseline, the average of the other three, the pushes become +6.0, +4.6, -5.1 and -5.6: good tries up, bad tries down.

![Cars with push arrows](../assets/clip-example.mp4)

*Watch the arrows. First (blue) they are almost equal, since every return is large. Then each shows its difference from the others' average: green up, red down.*

## Build It

The task is a 1-D reach: steering `a` moves the car from `x` to `x' = x + 0.2*a`, and each step pays `3 - x'^2 - 0.01*a^2`. The baseline for episode `i` at time `t` is the mean reward-to-go (rewards from step `t` to the end) of the other episodes, so it never sees its own action.

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

Compare gradient variance across seeds before comparing final returns.

Sources: OpenAI Spinning Up, "Intro to Policy Optimization", opened 2026-11-09. It states that a state-only baseline leaves the expected gradient unchanged and cuts its variance, and that reward-to-go removes zero-mean noise terms.

## Ship It

`outputs/skill-policy-gradient-debug.md` lists what to measure when a policy-gradient run is unstable.

## Exercises

1. Try `BONUS` 0 and 10 and plot the raw-versus-baseline gap.
2. Make `SIGMA` a learned parameter and derive its score term.
3. Replace the leave-one-out mean by the all-episode mean and test for bias at `batch=2`.
