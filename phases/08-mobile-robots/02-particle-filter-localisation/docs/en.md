# Particle Filter Localisation

> Learn how a lost robot, even one picked up and moved, finds where it is by keeping many guesses.

**Type:** Build   **Prerequisites:** 08/01 Differential Drive and Odometry   **Time:** ~15 minutes

## In Plain Words

A rover stands in a room with four posts and measures its distance to each. It keeps many guesses of where it is, copies the guesses that match, drops the rest and moves them all as far as it drove.

Now someone carries the rover to another corner. Every old guess is far from the new spot. A few random guesses across the room give new measurements something to find.

## Key Terms

- **Particle**: one guess of the robot's pose, `(x, y, heading)`.
- **Particle filter**: a crowd of particles that is moved, scored by measurements and resampled.
- **Landmark**: an object at a known place, like a post, whose distance the robot can measure.
- **Weight**: a score for how well a particle's predicted distances match the measured ones.
- **Resampling**: copying high-weight particles and dropping low-weight ones, keeping the count fixed.
- **Kidnap**: the robot is picked up and put somewhere else without being told.

## The Problem

Picture a robot in a building with two look-alike hallways. Odometry drifts, and one best guess cannot say "either hallway", but a cloud of guesses can. A cloud can also grow too sure of itself.

## The Concept

A real robot needs this to know where it is on a map and to recover after a slip or a lift.

![Particle filter cycle](../assets/diagram-pf-cycle.png)

*Move with noise, score, then copy or drop by score.*

A particle's weight grows as its predicted distances approach the measured ones (a Gaussian likelihood). Far from the truth every weight underflows to zero, so keep weights as logs and subtract the largest before `exp`. Systematic resampling draws `N` evenly spaced pointers from one random offset, so the cloud size stays fixed.

![Particles collapse](../assets/fig-pf-collapse.png)

*1000 particles, 4 landmarks: error below 0.3 m after 40 steps.*

![Kidnap diagram](../assets/diagram-pf-kidnap.png)

*After a kidnap no guess sits near the new pose.*

At step 40 the rover is carried 7.2 m, from `(2, 3)` to `(8, 7)`. One step later the plain filter's estimate is 3.79 m from the rover and ends 3.88 m away. With 5% random particles it is 0.43 m away and ends 0.24 m away.

![Plain and random clouds](../assets/clip-example.mp4)

*Tall blue (plain) never finds the lifted rover. Short green (5% random) jumps to it.*

![Error after kidnap](../assets/fig-pf-kidnap.png)

*Orange (plain) stays above 1.4 m. Blue (5% random) recovers, with a slightly noisier estimate.*

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

Nav2's AMCL localises a robot on a known map from a 2D laser scan. Compare its cloud spread with this lesson's.

Sources: Nav2 `nav2_amcl` README, github.com/ros-navigation/navigation2, opened 2026-11-09.

## Ship It

`outputs/skill-particle-filter-check.md` reviews a particle filter for depletion and kidnap handling.

## Exercises

1. Plot `n_eff` (how many particles still matter) and resample only below N/2.
2. Remove the max-subtraction; find where weights underflow.
3. Put the landmarks on one line and see which direction stays ambiguous.
