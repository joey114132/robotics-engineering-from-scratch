# Multimodal Demonstrations and Action Chunks

> Learn why a robot trained on two different good answers can pick a bad middle one, and how to make it pick one.

**Type:** Build   **Prerequisites:** 13/01 Imitation, 13/02 Cloning Pitfalls   **Time:** ~15 minutes

## In Plain Words

Half the demonstrations take a rover above a pillar and half below it. Both work, but a rule that averages the two steers straight at the pillar.

A chunk is the next few steps copied from one demonstration, so the rover commits to one side. A new chunk must agree with the old one, or the blend cancels the detour.

## Key Terms

- **Multimodal**: having several different correct answers, called modes.
- **Mean policy**: a policy that predicts the average action of nearby demonstrations.
- **Action chunk**: a short run of the next `H` actions, chosen together.
- **Sampler**: picks one demonstration at random instead of averaging.
- **Jitter**: the step-to-step change in action. High jitter looks like wobble.
- **Gaussian kernel**: a weight that is larger for demonstration states nearer the current one.

## The Problem

To get a rover past a pillar, half your demonstrations go above it and half below. Both are fine, but a policy that averages them drives straight into the pillar.

## The Concept

People solve one task in different ways, and a robot copying them must still pick one.

![Average or commit](../assets/diagram-average-or-commit.png)

*Both answers are right at the start, but their mean is wrong.*

For "up" and "down" demos a regression predicts "straight": at the start they steer +0.054 and -0.054 sideways, so the mean is 0. A sampler copies one demonstration instead, so both modes survive. Picking afresh each step can switch sides, so it returns a whole chunk of the next `H` actions.

![Chunk overlap](../assets/diagram-chunk-overlap.png)

*A new chunk starts before the old one ends. Overlapping steps blend from old to new.*

![Chunk fan](../assets/fig-chunk-fan.png)

*Left: the mean policy goes straight through. Middle: 40 sampled rollouts split both ways. Right: from H = 2 on, jitter falls under half.*

In 50 runs, one-step sampling clears the pillar 98% of the time with jitter 0.034 per step. Chunks of 8 steps, a new one every 4, clear it 100% with jitter 0.011.

![Steps vs chunks](../assets/clip-example.mp4)

*Blue picks a demonstration every step and wobbles. Green follows chunks and glides.*

## Build It

`mean_policy` weights nearby demonstration actions with a Gaussian kernel. `sample_chunk` picks one demonstration the same way and returns its next `H` actions.

```python
j = ((P[:, :-1] - x) ** 2).sum(2).argmin(1)            # nearest state in each demo
logw -= ((chunks[:, :len(prefix)] - prefix) ** 2).sum((1, 2)) / (2 * SIGMA_A**2)
a = w * new[k] + (1 - w) * old[k + stride]             # blend while chunks overlap
```

Without `prefix`, the blend can head at the disc.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks -q
python3 phases/13-learning-for-robots/06-multimodal-demos-and-action-chunks/code/figure.py
```

## Use It

Real policies use a network that outputs a chunk. A longer chunk reacts more slowly.

Sources (abstracts, 2026-11-10): Zhao et al., arXiv:2304.13705; Chi et al., arXiv:2303.04137.

## Ship It

`outputs/skill-multimodal-demo-check.md` finds modes a mean policy would average.

## Exercises

1. Make the split 5 to 1. What does the mean policy do?
2. Set `SIGMA_A` large and count rollouts hitting the disc.
3. Add action noise. At what chunk length does jitter stop falling?
