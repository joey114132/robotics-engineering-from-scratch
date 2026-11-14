# Particle Filter Localisation

> Keep many guesses of where you are, let the measurements kill the bad ones, and keep a few wild guesses for the day you are moved.

**Type:** Build   **Prerequisites:** 08/01 Differential Drive and Odometry   **Time:** ~15 minutes

## In Plain Words

A rover stands in a room with four posts (landmarks) and measures its distance to each one. It keeps many guesses of where it is, copies the guesses whose distances match, and drops the rest. It moves every guess as far as it drove. This crowd of guesses is a particle filter.

Now someone carries the rover to another corner. Every old guess is far from the new spot, so copying them cannot help. A few random guesses across the room give new measurements something to find.

## The Problem

Odometry drifts, so a robot on a known map needs outside measurements to say where it is. One Gaussian (a single bump of belief) cannot hold "I could be in either corridor", but a cloud of guesses can. The cloud's own failure: it can grow too sure of itself to be corrected.

## The Concept

![One cycle of a particle filter](../assets/diagram-pf-cycle.png)

*Each guess is moved with noise, scored by how well its landmark distances match the measured ones, then copied or dropped in proportion to its score.*

A guess is a particle: a pose `(x, y, heading)`. Its weight says how well it fits: the closer its predicted distances are to the measured ones, the bigger (a Gaussian likelihood). Far from the truth every weight is so tiny it rounds to zero (underflow), so we keep weights as logs and subtract the largest before `exp`. Systematic resampling copies guesses in proportion to weight, drawing `N` evenly spaced pointers from one random offset, which keeps the cloud size fixed.

![Particles collapsing onto the true pose](../assets/fig-pf-collapse.png)

*Blue dots are guesses, the orange star the true pose. With 1000 particles and 4 landmarks the cloud shrinks onto the star in a few steps, and the error after 40 steps is below 0.3 m.*

![A collapsed cloud cannot find a moved robot](../assets/diagram-pf-kidnap.png)

*After a kidnap (the robot is carried away) every guess fits badly, and none sits near the new pose.*

In the lesson's kidnap run the rover is carried 7.2 m, from `(2, 3)` to `(8, 7)`, at step 40. "Off" means estimate to rover. One step later the plain filter is 3.79 m off and ends 3.88 m off. With 5% random particles it is 0.43 m off and ends 0.24 m off.

![Plain and random-particle clouds after a kidnap](../assets/clip-example.mp4)

*Watch the amber rover lifted away. Each thin marker is one guess: tall blue (plain filter) never finds it, short green (5% random) jumps to it. Dark posts are landmarks.*

![Error after a kidnap with and without random particles](../assets/fig-pf-kidnap.png)

*Orange (plain filter) never gets back below 1.4 m. Blue (5% random particles each step) recovers, at the price of a slightly noisier estimate.*

## Build It

```python
def log_weights(P, z, sigma, lm=LANDMARKS):
    return -0.5 * (((ranges(P, lm) - z) / sigma) ** 2).sum(axis=1)

def systematic_resample(w, rng):
    n = len(w)
    idx = np.searchsorted(np.cumsum(w), (rng.random() + np.arange(n)) / n)
    return np.minimum(idx, n - 1)
```

`pf_step()` chains predict, weight, resample and optional injection.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/02-particle-filter-localisation -q
python3 phases/08-mobile-robots/02-particle-filter-localisation/code/figure.py
```

## Use It

Nav2's AMCL localises a robot on a known map with a 2D laser scanner and has a `random_seed` for repeatable runs. Compare its cloud spread with this lesson's.

Sources: Nav2 `nav2_amcl` README, github.com/ros-navigation/navigation2, opened 2026-11-09.

## Ship It

`outputs/skill-particle-filter-check.md` reviews a particle filter for depletion and kidnap handling.

## Exercises

1. Plot `n_eff` over time and resample only when it drops below N/2.
2. Remove the max-subtraction and find the step where the weights underflow.
3. Make the landmarks collinear and see which direction stays ambiguous.
