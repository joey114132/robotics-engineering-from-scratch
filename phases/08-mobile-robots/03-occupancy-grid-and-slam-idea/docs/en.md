# Occupancy Grid and the SLAM Idea

> Learn how a robot draws a room map from laser beams, and why a small heading error ruins it.

**Type:** Build   **Prerequisites:** 08/01 Differential Drive and Odometry   **Time:** ~15 minutes

## In Plain Words

A rover measures a room with laser beams. A beam ends at the first thing it hits. The floor it crossed is empty, its end is an obstacle, and behind is unknown. An occupancy grid keeps this in map squares.

If the rover's heading guess worsens every step, obstacles land in the wrong squares. Scans then smear the map. SLAM fixes the rover's position using the map so far.

## Key Terms

- **Scan**: one sweep of laser beams.
- **Occupancy grid**: a map split into small squares, each holding a score for "something is here".
- **Log-odds (`L`)**: a square's evidence score. Positive means probably occupied, negative probably free, and 0 unknown.
- **SLAM**: drawing the map and finding your place on it at the same time.
- **Heading**: the direction the robot faces.
- **Drift**: a small error that adds up step after step.

## The Problem

Picture a robot's map after one lap of a room: every wall twice, slanted, with a ghost room beside it. The scanner was fine; the robot drew each scan from a wrong place.

## The Concept

A robot plans routes with its map, so a smeared map breaks what follows.

The map is a grid of small squares. Each laser beam marks the squares it crossed as probably empty and the square where it stopped as probably wall. Seeing a wall again and again makes it certain.

![Beam update](../assets/diagram-beam-update.png)

*Empty before the wall, wall at the end.*

![Pillars grow](../assets/clip-example.mp4)

*Each pillar is a cell's score. Walls rise, floor sinks.*

This only works if the robot knows where it stood at each scan. A growing heading error smears the walls.

![Three maps](../assets/fig-grid-maps.png)

*Left: the room. Middle: map from true positions. Right: map from drifted positions.*

![Mapping and pose loop](../assets/diagram-slam-loop.png)

*The map fixes the position; the position adds to the map.*

![Wall quality curve](../assets/fig-smear-curve.png)

*The share of real wall squares falls fast as heading error grows.*

<details><summary>The math (optional)</summary>

Each cell holds a score `L` (log-odds): positive means probably occupied, negative probably free, 0 unknown. A beam end adds 0.85 and a crossed cell subtracts 0.4. `L` is clamped at +-5 so a changed world can still be learned, and `p = 1 - 1 / (1 + exp(L))` gives the probability. After three scans a wall cell has `L = 2.55` (`p = 0.93`) and a floor cell `L = -1.2` (`p = 0.23`). With 200 scans, a heading error of 0.003 rad per step (34° over the loop) leaves only 41% of occupied cells real. Under 6 degrees the real share already falls from 0.89 to 0.62.

</details>

## Build It

```python
def update(L, pose, r, angles, max_range=8.0):
    ...  # cells crossed: L -= 0.4, cell where each beam ended: L += 0.85
    return np.clip(L, -L_MAX, L_MAX).reshape(N, N)

def drift(poses, yaw_err):
    way = np.arctan2(d[:, 1], d[:, 0]) + yaw_err * k[1:]
```

`scan()` sends beams through a hidden world. `build_map()` places scans at the positions you give it.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/03-occupancy-grid-and-slam-idea -q
python3 phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/code/main.py
```

## Use It

Nav2, a robot-navigation package, loads and saves grid maps like this one.

Sources: Nav2 `nav2_map_server` README, github.com/ros-navigation/navigation2, opened 2026-11-09.

## Ship It

`outputs/skill-occupancy-grid-check.md` diagnoses a smeared or doubled map.

## Exercises

1. Make the laser noisier; watch the walls thicken.
2. After one scan, count the squares that are neither empty nor wall.
3. Give one scan a wrong position; see the damage.
