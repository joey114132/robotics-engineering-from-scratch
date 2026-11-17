# Extended Kalman Filter

> Learn how a robot that drives in curves tracks its position, and why a wrong start can leave it confidently wrong.

**Type:** Build   **Prerequisites:** 07/02 Kalman Filter   **Time:** ~15 minutes

## In Plain Words

A robot drives along a curved path and measures how far a post is. A filter, the program that tracks where the robot is, pretends a short piece of that curve is straight. This works only near where the robot really is. Far off, the filter still says it is nearly sure while its real error grows.

## Key Terms

- **EKF**: extended Kalman filter, a program that tracks where the robot is, using a straight-line rule at its current guess.
- **Linearise**: replace a curve by its straight-line approximation at one point.
- **Heading**: the direction the robot faces.
- **Jacobian (`F`, `H`)**: a table of slopes. It says how much the filter's prediction changes when the robot's position and heading change a little.
- **Landmark**: a post at a known place that the robot measures.
- **NEES**: a score for whether the filter's doubt matches its real error. An honest filter scores about 3 here, one per value it tracks.

## The Problem

A robot on a curved path tracks itself with one post as a landmark. Its heading guess starts wrong, and the filter drifts away while saying it is nearly sure.

## The Concept

A confidently wrong robot is more dangerous than an unsure one.

![One EKF cycle](../assets/diagram-ekf-loop.png)

*The straight-line rule is rebuilt each cycle.*

A Kalman filter needs straight-line motion, but the robot's real path is a curve. The extended filter pretends a short piece of the curve around its current guess is straight, and redraws that piece every cycle.

![Bad linearisation feeds itself](../assets/diagram-ekf-spiral.png)

*A wrong heading gives a wrong rule, a wrong correction, a worse heading.*

NEES checks whether the filter's claimed doubt matches its real error.

![NEES against heading error](../assets/fig-ekf-run.png)

*Left: the EKF follows the truth. Right: with four landmarks NEES stays near the dashed line (3); with one it climbs far above as the start error grows.*

![One post, four posts](../assets/clip-example.mp4)

*Both start with a wrong heading. This picture compares one post (blue) with four (green); the lead clip uses three. With one post the guess ends far off while its small circle says the filter is sure. With four it stays on the robot.*

<details><summary>The math (optional)</summary>

The state is `[x, y, heading]`; the robot moves along a curve `f(x, u)` with speed `v` and turn rate `w`. `F` is the Jacobian of the motion, `H` that of the landmark's range and bearing `h(x)`. Covariance is predicted by `P = F P F^T + Q`. Bearing differences are wrapped. NEES is `e^T P^-1 e` and averages the state size, 3 (two for position, one for heading). With a heading guess 1 rad off and one landmark, NEES averages 100.5 over 30 runs and the estimate ends 2.8 m off. With four it averages 2.7. In the figure NEES stays near 3 with four landmarks and grows from about 4 to several hundred with one. Tests check NEES near 3 over 150 seeds, and over 20 times larger with one landmark and a 1.5 rad heading error. 1 m is drawn as 0.5 m.

</details>

## Build It

```python
def jac_h(x, lm):
    dx, dy = lm - x[:2]
    q, r = dx*dx + dy*dy, np.hypot(dx, dy)
    return np.array([[-dx/r, -dy/r, 0], [dy/q, -dx/q, -1]])

H = jac_h(x, lm)                       # at the estimate
K = P @ H.T @ np.linalg.inv(H @ P @ H.T + R)
y = z - h(x, lm); y[1] = wrap(y[1])
x = x + K @ y
```

Tests check both Jacobians against a numeric slope.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/05-extended-kalman-filter -q
python3 phases/07-state-estimation/05-extended-kalman-filter/code/main.py
```

## Use It

`robot_localization`, a robot-software package, ships `ekf_node`.

Sources: robot_localization state estimation nodes, https://docs.ros.org/en/melodic/api/robot_localization/html/state_estimation_nodes.html (2026-11-09), and the `ekf_node` target in its `CMakeLists.txt`, https://github.com/cra-ros-pkg/robot_localization (2026-11-10).

## Ship It

`outputs/skill-ekf-consistency-check.md` reviews an EKF for overconfidence.

## Exercises

1. Drop the minus sign in `jac_f` (the motion Jacobian) and watch NEES.
2. Add a second landmark and watch NEES.
3. Make the motion-noise number `Q` four times bigger and compare NEES.
