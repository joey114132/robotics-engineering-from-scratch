# Bayes Filter

> Learn how a robot keeps track of where it is when its wheels slip and its sensors are vague.

**Type:** Build   **Prerequisites:** none   **Time:** ~15 minutes

## In Plain Words

A robot rolls around a ring corridor. Its wheels slip, so it grows less sure where it is. Picture a bar over each spot, taller where the robot probably is. A "door" reading raises the bars over doors.

## Key Terms

- **Belief**: how likely the robot thinks each place is, one probability per place.
- **Predict**: the step that slides and blurs the belief by the move, adding doubt.
- **Update**: the step that reweights the belief by how well each place explains a reading.
- **Prior / posterior**: the belief before and after a reading.
- **Likelihood**: how well a place explains a sensor reading.
- **Entropy**: a score of doubt, high when all places look equally likely.

## The Problem

A robot counts wheel turns to find its place in a corridor. After a hundred steps the slipping count is a guess and it enters the wrong door, and one "door" reading fits several places.

## The Concept

A robot never knows its position for sure, so it tracks how likely each place is.

![Bayes filter step](../assets/diagram-bayes-cycle.png)

*Predict shifts and blurs. Update reweights by the reading.*

The belief is a row of bars, one per corridor cell, taller where the robot is likelier to be. Predict slides the bars by the move and blurs them, because wheels slip. Update raises the bars for cells that agree with the sensor reading and lowers the others, then rescales so the bars add up to one. This step is Bayes' rule.

![Rover finds its cell](../assets/clip-example.mp4)

*Moves slide and blur the green bars, readings (door: amber lamp) make them jump. The rover's cell ends up with most of the belief.*

![Filter against dead reckoning](../assets/diagram-bayes-split.png)

*Dead reckoning (wheel counts alone, no sensor step): the belief keeps spreading.*

![Belief locks on](../assets/fig-belief-sharpening.png)

*Left: probability gathers on the true cell after a few doors. Right: doubt falls.*

![Doubt without the sensor](../assets/fig-dead-reckoning.png)

*Left: motion-only doubt keeps rising. Right: the simulation matches the growth the formula gives.*

<details><summary>The math (optional)</summary>

Predict blurs by wheel slip: 5% short, 90% exact, 5% long. Update: `posterior = prior * likelihood / sum`. A cell that agrees with the reading gets weight `p_hit = 0.9`, one that disagrees `0.1`. With all 20 cells at 0.05 and 8 doors, "door" makes a door cell `0.05 * 0.9 = 0.045` and a wall cell `0.05 * 0.1 = 0.005`. The sum is `8 * 0.045 + 12 * 0.005 = 0.42`, so a door cell ends at 0.107 and a wall cell at 0.012. After five moves the rover's cell holds 0.86. Entropy falls from ln 20 (about 3) toward 1. Each predict adds `0.05 + 0.05 = 0.1` cell^2 of variance.

</details>

## Build It

```python
def predict(bel, move, kernel=KERNEL):
    return sum(p * np.roll(bel, move + k) for k, p in zip((-1, 0, 1), kernel))

def update(bel, z, doors=DOORS, p_hit=P_HIT):
    post = bel * np.where(doors == z, p_hit, 1 - p_hit)
    return post / post.sum()
```

The corridor is a ring of 20 cells, so `np.roll` wraps the ends around.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/01-bayes-filter -q
```

## Use It

AMCL, from Nav2 (the navigation package for ROS 2), stores the same belief as many sample points (a particle filter).

Sources: Nav2 AMCL README, https://github.com/ros-navigation/navigation2/blob/main/nav2_amcl/README.md (2026-11-09).

## Ship It

`outputs/skill-bayes-filter-check.md` reviews a localizer.

## Exercises

1. Change the slip chances and watch the blur.
2. Set the chance a door reading is right (`p_hit`) close to 1 and try one bad reading.
3. Try a corridor with walls.
