# Multimodal Demonstrations and Action Chunks

> Learn why a robot trained on two different good answers can pick a bad middle one, and how to make it pick one.

**Type:** Build   **Prerequisites:** 13/01 Imitation, 13/02 Cloning Pitfalls   **Time:** ~15 minutes

## In Plain Words

Half the demonstrations take a rover above a pillar and half below it. Both work, but a rule that averages the two steers straight at the pillar.

A chunk is the next few steps copied from one demonstration, so the rover commits to one side. A new chunk must agree with the old one, or the blend cancels the detour.

## Key Terms

- **Multimodal**: having several different correct answers, called modes.
- **Mean policy**: a policy that predicts the average of nearby demonstrations.
- **Action chunk**: the next few actions, chosen together.
- **Sampler**: picks one demonstration at random instead of averaging.
- **Jitter**: how much the action changes from step to step. High jitter looks like wobble.
- **Gaussian kernel**: a weight that is larger for demonstrations closer to where the robot is now.

## The Problem

To get a rover past a pillar, half your demonstrations go above it and half below. Both are fine, but a policy that averages them drives straight into the pillar.

## The Concept

People solve one task in different ways, and a robot copying them must still pick one. Picking one demonstration avoids the bad average, but picking again every step can flip sides and wobble. So the robot picks a short chunk of the next few moves and follows it.

![Average or commit](../assets/diagram-average-or-commit.png)

*Both answers are right at the start, but their average is wrong.*

![Chunk overlap](../assets/diagram-chunk-overlap.png)

*A new chunk starts before the old one ends, and the overlap blends from old to new.*

![Chunk fan](../assets/fig-chunk-fan.png)

*Left: the average goes straight through the pillar. Middle: sampling splits both ways round. Right: longer chunks wobble less.*

![Steps vs chunks](../assets/clip-example.mp4)

*Blue picks a demonstration every step and wobbles. Green follows chunks and glides.*

<details><summary>The math (optional)</summary>

At the start the two demonstrations steer +0.054 and -0.054 sideways, so the mean is 0. Over 50 runs, one-step sampling clears the pillar 98% of the time with jitter 0.034 per step. Chunks of 8 steps, a new one every 4, clear it 100% with jitter 0.011. With chunks of 2 or more, jitter falls under half and all 60 rollouts clear the disc. Each demonstration's weight comes from a Gaussian kernel on how close it passes. Without a `prefix` that matches the old chunk, the blend can head at the disc. If the split is 5 to 1, the sampler goes over about five times in six.

</details>

## Build It

`mean_policy` averages nearby demonstrations. `sample_chunk` picks one demonstration instead and returns its next few actions.

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

Real policies use a neural network that outputs a whole chunk. A longer chunk reacts more slowly.

Sources (abstracts, 2026-11-10): Zhao et al., arXiv:2304.13705; Chi et al., arXiv:2303.04137.

## Ship It

`outputs/skill-multimodal-demo-check.md` finds modes a mean policy would average.

## Exercises

1. Make the demonstrations split 5 to 1. What does the average do?
2. Make the choice very loose and count rollouts that hit the pillar.
3. Add noise to the actions. At which chunk length does the wobble stop falling?
