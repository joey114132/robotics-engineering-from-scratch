# Kalman Filter

> When a model and a noisy sensor disagree, the Kalman gain decides how far to move toward the sensor, and it also tells you how wrong the result still is.

**Type:** Build   **Prerequisites:** 07/01 Bayes Filter   **Time:** ~15 minutes

## In Plain Words

At a skating rink, you estimate where a friend is from their last position and speed. A shouted position
report arrives with some error. If the report is usually unreliable, you move your estimate toward it only a
little; if your motion prediction is uncertain, you correct more.

The Kalman gain sets that balance. The filter updates estimated position and velocity, while covariance tracks
its remaining uncertainty. A corrected estimate is still a guess, and its uncertainty should match errors
measured over repeated trials.

## The Problem

A position sensor is off by about 2 m on every reading. Plotting its raw output makes the robot look as if it jitters, and differencing it for speed makes the jitter worse. Averaging the last few readings removes the jitter but lags behind every turn.

## The Concept

![One Kalman cycle](../assets/diagram-kalman-loop.png)

*Predict with the motion model, then correct with the reading. The corrected estimate feeds the next cycle.*

The state is `x = [position, velocity]` and velocity changes by small random accelerations. Predict: `x = F x`, `P = F P F^T + Q`. A reading `z = H x + noise` has variance `R`. The correction is `x = x + K (z - H x)`, and its error covariance in Joseph form is `P = (I - K H) P (I - K H)^T + K R K^T`. Setting the derivative of its trace to zero gives `K = P H^T (H P H^T + R)^-1`.

![The gain is a trust dial](../assets/diagram-kalman-trust.png)

*Big sensor noise makes K small and the filter follows its model. Large model uncertainty makes K large and the filter follows the sensor.*

![Estimate, band and measured error](../assets/fig-kalman-band.png)

*Left: one run, with the estimate inside its 2-sigma band. Right: over 4000 runs the actual error settles near 1.0 m, half the raw 2.0 m, and sits on the filter's own `sqrt(P)`.*

## Build It

```python
def gain(P, H, R):
    return P @ H.T @ np.linalg.inv(H @ P @ H.T + R)

x, P = F @ x, F @ P @ F.T + Q        # predict
K = gain(P, H, R)
x = x + K @ (z[None, :] - H @ x)     # update
P = (np.eye(2) - K @ H) @ P
```

Tests check that perturbing `K` raises the Joseph trace, that the error covariance over 4000 runs equals `P`, and that about 95% of errors fall inside 2 sigma.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/02-kalman-filter -q
```

## Use It

ROS's `robot_localization` ships `ekf_localization_node`, an extended Kalman filter that projects a motion model forward and corrects it with sensor data. SciPy's `solve_discrete_are` gives the steady-state `P`, and the last test compares it with the loop above.

Sources: robot_localization state estimation nodes, https://docs.ros.org/en/melodic/api/robot_localization/html/state_estimation_nodes.html (opened 2026-11-09).

## Ship It

`outputs/skill-kalman-filter-check.md` reviews a filter for the usual silent mistakes in `Q`, `R` and `P`.

## Exercises

1. Double `R_STD` and predict, before running, whether the steady-state `sqrt(P)` rises or falls.
2. Feed the filter `R` ten times too small and compare the 2-sigma coverage with 95%.
3. Set `SA` to 0 and watch `K` shrink toward zero until the filter ignores the sensor.
