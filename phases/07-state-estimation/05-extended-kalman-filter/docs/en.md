# Extended Kalman Filter

> Linearise the model at your current estimate and run a Kalman filter on that, which works only while the estimate is close enough to the truth.

**Type:** Build   **Prerequisites:** 07/02 Kalman Filter, 08/01 Differential Drive and Odometry   **Time:** ~15 minutes

## In Plain Words

Find your way across a playground using your guessed heading and the distance and direction to a tree.
Your prediction of how those readings change after a small step depends on where you think you stand. A
badly wrong heading can turn a plausible correction into another mistake.

An extended Kalman filter linearises motion and measurements at its current estimate, since the true
state is unknown. That local approximation can fail far from the truth. The filter may report shrinking
uncertainty even as its actual error grows.

## The Problem

The Kalman filter of 07/02 needs `x' = F x`. A robot that turns has a heading inside every `cos` and `sin`, so no constant `F` exists. You feed the filter a landmark reading anyway, and with a good start it works. With a heading guess that is 1 rad off and a single landmark in view, it drifts away while reporting a small covariance.

## The Concept

![One EKF cycle](../assets/diagram-ekf-loop.png)

*Both Jacobians are evaluated at the current estimate, because the true state is unknown.*

The state is `[x, y, heading]` and the robot moves with speed `v` and turn rate `w`. The motion is `f(x, u)`, and `F` is its matrix of partial derivatives. A landmark at a known place gives range and bearing, `h(x)`, with Jacobian `H`. Covariance is predicted with `P = F P F^T + Q` and corrected with the Kalman update using `H`. The bearing difference must be wrapped into `[-pi, pi]`.

![A bad linearisation point feeds on itself](../assets/diagram-ekf-spiral.png)

*A wrong heading gives a wrong Jacobian, which gives a wrong correction, which leaves the heading wronger.*

Consistency is measured by NEES, `e^T P^-1 e`. Averaged over runs it should equal the state dimension, 3.

![One run and NEES against the initial heading error](../assets/fig-ekf-run.png)

*Left: the EKF follows the truth while dead reckoning bends away. Right: with four landmarks NEES stays near 3, and with one landmark it grows from about 4 to several hundred.*

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

Tests compare both Jacobians with finite differences, check NEES near 3 over 150 seeds, and check that one landmark plus a 1.5 rad heading error blows NEES up by more than 20 times.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/05-extended-kalman-filter -q
python3 phases/07-state-estimation/05-extended-kalman-filter/code/main.py
```

## Use It

The ROS package `robot_localization` ships an EKF node (`ekf_node` in its ROS 2 branch, `ekf_localization_node` in the older ROS 1 docs), an extended Kalman filter for exactly this predict-and-correct loop. Compare its covariance behaviour with the NEES check here.

Sources: robot_localization state estimation nodes, https://docs.ros.org/en/melodic/api/robot_localization/html/state_estimation_nodes.html (opened 2026-11-09), and the `ekf_node` target in the package's `CMakeLists.txt`, https://github.com/cra-ros-pkg/robot_localization (opened 2026-11-10).

## Ship It

`outputs/skill-ekf-consistency-check.md` reviews an EKF for wrong Jacobians, unwrapped angles and overconfident covariance.

## Exercises

1. Break `jac_f` by dropping the minus sign and watch NEES.
2. Add a second landmark to the one-landmark case and find the smallest heading error that still diverges.
3. Inflate `Q` by 4 and compare NEES with 3.
