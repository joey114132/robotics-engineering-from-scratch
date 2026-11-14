# Occupancy Grid and the SLAM Idea

> A map is only as good as the poses you drew it from, which is why mapping and localising have to be solved together.

**Type:** Build   **Prerequisites:** 08/01 Differential Drive and Odometry   **Time:** ~15 minutes

## In Plain Words

A rover in a room with a box measures distances with laser beams. Each beam ends at the first thing it hits: the floor crossed is empty, its end is an obstacle, and behind is unknown. An occupancy grid keeps this evidence in map squares.

Suppose the rover's heading estimate is slightly off and worsens every step. The distances are right but the box lands in the wrong squares, so repeated scans smear the map. SLAM (mapping and locating at once) corrects the pose using the map so far.

## The Problem

You drive a laser robot around a room once and the saved map shows every wall twice, slanted, with a ghost room beside it. The scanner was fine. The robot drew each scan from a place it wrongly believed it was in.

## The Concept

![What one laser beam tells the grid](../assets/diagram-beam-update.png)

*One beam lowers the score of the cells it crossed, raises the cell where it ended, and says nothing about what lies behind.*

An occupancy grid stores one evidence score `L` per cell, the log-odds of "occupied". Positive means probably occupied, negative probably free, and 0 unknown. A beam end is strong evidence, so it adds `0.85`. A crossed cell is weaker evidence of free, so it subtracts `0.4`. `L` is capped at `+-5`, and `p = 1 - 1 / (1 + exp(L))` turns it into a probability. Each cell is touched once per scan, so many beams do not count a wall twice.

After three scans, a wall cell hit every time has `L = 3 x 0.85 = 2.55`, so `p = 0.93`. A floor cell crossed every time has `L = 3 x -0.4 = -1.2`, so `p = 0.23`.

![Pillars grow as a rover scans a wall](../assets/clip-example.mp4)

*Pillar height is the size of `L`: each scan lifts amber wall pillars (more occupied) by 0.85 and green floor pillars (more free) by 0.4.*

![True room, known-pose map and drifted map](../assets/fig-grid-maps.png)

*Left: the room. Middle: 200 scans from known poses. Right: the same scans with a heading that gains 0.003 rad per step (34° over the loop); only 41% of the occupied cells are real.*

![Mapping needs the pose and the pose needs the map](../assets/diagram-slam-loop.png)

*SLAM closes the circle: draw the scan at the pose, match the next scan to the map so far, correct the pose, draw again.*

![Wall quality against heading error](../assets/fig-smear-curve.png)

*Heading error is the total turn error over the loop. Under 6 degrees already cuts the real share of occupied cells from 0.89 to 0.62.*

The drift model keeps step lengths exact and adds a small heading error every step.

## Build It

```python
def update(L, pose, r, angles, max_range=8.0):
    ...  # cells crossed: L -= 0.4, cell where each beam ended: L += 0.85
    return np.clip(L, -L_MAX, L_MAX).reshape(N, N)

def drift(poses, yaw_err):
    way = np.arctan2(d[:, 1], d[:, 0]) + yaw_err * k[1:]
```

`scan()` sends beams through a hidden true world. `build_map()` places scans at the poses you give it, true or drifted.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/03-occupancy-grid-and-slam-idea -q
python3 phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/code/main.py
```

## Use It

Nav2's map server loads and saves `nav_msgs/msg/OccupancyGrid` maps, the format its navigation stack reads. A real mapping package estimates poses and grid together.

Sources: Nav2 `nav2_map_server` README, github.com/ros-navigation/navigation2, opened 2026-11-09.

## Ship It

`outputs/skill-occupancy-grid-check.md` diagnoses a smeared or doubled map.

## Exercises

1. Raise the beam noise and find when walls become two cells thick.
2. Add a `p < 0.35` free threshold and count unknown cells.
3. Give only the last scan a bad pose and see how local the damage is.
