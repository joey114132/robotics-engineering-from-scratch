# Bayes Filter

> A robot never knows where it is, only how likely each place is, and two steps keep that belief honest: predict adds doubt, update removes it.

**Type:** Build   **Prerequisites:** 01/04 Frames and Transform Trees   **Time:** ~15 minutes

## The Problem

A robot rolls down a corridor and counts its wheel turns to know where it is. Wheels slip a little, so after a hundred steps the count is a guess, and the robot walks into the wrong door. Throwing the count away is no better: one reading of "door" fits several places.

## The Concept

![One step of the Bayes filter](../assets/diagram-bayes-cycle.png)

*Predict shifts the belief by the move and blurs it. Update multiplies by how well each cell explains the reading.*

The belief is a histogram: one probability per corridor cell. Predict convolves it with a motion kernel, here 5% short, 90% exact, 5% long. Update uses Bayes' rule, `posterior = prior * likelihood / sum`, where a cell that agrees with the reading is weighted by `p_hit = 0.9` and a cell that disagrees by `0.1`.

![Dead reckoning against the filter](../assets/diagram-bayes-split.png)

*Without the sensor step the belief keeps spreading. With it the belief stays near the truth.*

![Belief locks on as readings arrive](../assets/fig-belief-sharpening.png)

*Left: starting from a flat belief, the mass collects on the true cell after a few doors. Right: entropy falls from ln 20 toward 1 nat.*

![Doubt grows without the sensor](../assets/fig-dead-reckoning.png)

*Left: entropy of motion-only belief keeps rising, the filter's stays flat. Right: each predict adds `0.05 + 0.05 = 0.1` cell^2 of variance, matched by simulation.*

## Build It

```python
def predict(bel, move, kernel=KERNEL):
    return sum(p * np.roll(bel, move + k) for k, p in zip((-1, 0, 1), kernel))

def update(bel, z, doors=DOORS, p_hit=P_HIT):
    post = bel * np.where(doors == z, p_hit, 1 - p_hit)
    return post / post.sum()
```

The corridor is a ring of 20 cells so `np.roll` handles the ends. The full file adds `entropy`, `simulate` and `run`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/01-bayes-filter -q
```

## Use It

A particle filter stores the same belief as samples instead of a histogram, which scales to a 2-D map. Nav2's AMCL (Adaptive Monte Carlo Localization) estimates a robot's pose in a known map using a 2D laser scanner. Compare its pose spread with this lesson's entropy as the robot moves.

Sources: Nav2 AMCL README, https://github.com/ros-navigation/navigation2/blob/main/nav2_amcl/README.md (opened 2026-11-09).

## Ship It

`outputs/skill-bayes-filter-check.md` reviews a localizer for a missing predict or update step.

## Exercises

1. Change `KERNEL` to `(0.2, 0.6, 0.2)` and predict the variance after 10 steps before running it.
2. Feed the filter a wrong `p_hit` of 0.99 and watch what a single bad reading does.
3. Replace the ring with a corridor that has two walls and decide where the lost mass goes.
