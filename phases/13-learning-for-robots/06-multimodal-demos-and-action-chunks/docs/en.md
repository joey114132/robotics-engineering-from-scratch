# Multimodal Demonstrations and Action Chunks

> When demonstrations disagree, a regression averages them into an action nobody demonstrated, and a short chunk of future actions commits to one.

**Type:** Build   **Prerequisites:** 13/01 Imitation, 13/02 Cloning Pitfalls   **Time:** ~15 minutes

## In Plain Words

Carry a tray past a cafeteria table. Going left or right can both work, but averaging the directions can send you straight into the
table. Switching sides after every step can also make you hesitate and zigzag.

Multimodal demonstrations contain that same split. Sampling an action chunk chooses a short sequence from one route, instead of
averaging opposing routes. When chunks overlap, choosing a new one that agrees with the unfinished sequence lets their actions blend
without cancelling the detour.

## The Problem

Half your demonstrations steer a point robot over an obstacle and half steer it under. Each demonstration is good, yet the policy trained on them drives straight into the obstacle. The first wrong action averages two valid answers for one observation. In 13/02, rollout distribution shift instead follows policy errors into unfamiliar states; those errors can compound without noise.

## The Concept

![Average or commit](../assets/diagram-average-or-commit.png)

*At the start, two answers are both right. Their mean is a third answer that is wrong. A sampler picks one demonstration and follows it.*

Least squares and kernel regression both predict the mean action. For a symmetric split the mean of "up" and "down" is "straight". Sampling instead keeps the data's two modes. A single sampled step can still flip sides, so the sampler returns a whole chunk of the next `H` actions and executes it.

![Chunk overlap](../assets/diagram-chunk-overlap.png)

*A new chunk starts before the old one ends. The overlapping steps are a weighted average, and the new chunk is chosen to agree with the old one.*

![Fan of rollouts and the chunk length](../assets/fig-chunk-fan.png)

*Left: the mean policy runs a straight line through the disc. Middle: 40 sampled rollouts split between the two ways round. Right: from H = 2 on, jitter falls to under half of the single-step value and all 60 rollouts clear the disc.*

## Build It

`mean_policy` weights nearby demonstration actions with a Gaussian kernel. `sample_chunk` picks one demonstration with that kernel and returns its next `H` actions.

```python
j = ((P[:, :-1] - x) ** 2).sum(2).argmin(1)            # nearest state in each demo
logw -= ((chunks[:, :len(prefix)] - prefix) ** 2).sum((1, 2)) / (2 * SIGMA_A**2)
a = w * new[k] + (1 - w) * old[k + stride]             # blend while chunks overlap
```

Without the `prefix` term, a new chunk can pick the other side, and the blend of the two heads straight at the disc.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks -q
python3 phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/code/figure.py
```

## Use It

Real policies replace the lookup with a network that outputs a chunk, and blend overlapping predictions at run time. A longer chunk reacts more slowly to what happens in between, so measure the cost on your task.

Sources: Zhao et al., "Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware", arXiv:2304.13705, abstract opened 2026-11-10: it learns a generative model over action sequences. Chi et al., "Diffusion Policy", arXiv:2303.04137, abstract opened 2026-11-10: it handles multimodal action distributions.

## Ship It

`outputs/skill-multimodal-demo-check.md` checks a demonstration set for modes that a mean policy would average.

## Exercises

1. Make the split 5 to 1 and find what the mean policy does.
2. Set `SIGMA_A` large and count the rollouts that hit the disc.
3. Add per-step action noise and find the chunk length where jitter stops falling.
