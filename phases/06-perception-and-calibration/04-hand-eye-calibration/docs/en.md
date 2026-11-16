# Hand-Eye Calibration

> Learn how to find where a camera is mounted on a robot's hand, and why the arm must turn about different axes.

**Type:** Build   **Prerequisites:** 01/04 Frames and Transform Trees, 06/01 Pinhole Camera   **Time:** ~15 minutes

## In Plain Words

A camera is bolted to a robot arm's hand. The arm must know where the camera sits on the hand, called X. Move the arm and compare how the hand moved with how the camera saw it. If every motion spins about one axis, sliding the camera along it changes nothing, so use different axes.

## Key Terms

- **Hand-eye calibration**: finding where a camera sits relative to the gripper it is mounted on.
- **Transform (`X`)**: the rotation and shift that take one frame to another, here camera to gripper.
- **Rotation axis**: the line a rotation spins about.
- **SVD**: a matrix tool, here used to line up two sets of axes.
- **Singular value**: a number from the SVD. A near-zero one flags a missing direction.
- **Spread**: the half-angle of the cone that the motions' axes fill.

## The Problem

A camera on a robot's hand sees a cup 0.4 m ahead, yet the gripper misses it. The camera's mounting `X` is unknown, and motions about one axis hide it.

## The Concept

Without `X`, nothing the camera sees can become a place the hand reaches.

![Why the equation is AX = XB](../assets/diagram-handeye-setup.png)

*Each motion is measured twice: `A` from the joints, `B` from the camera. `X` never changes.*

Each motion is a rotation `R` plus a translation `t`. Rotation: `R_A R_X = R_X R_B`, so `log(R_A) = R_X log(R_B)` (`log(R)` is axis times angle). An SVD gives `R_X`. Translation: `(R_A - I) t_X = R_X t_B - t_A`, linear in `t_X`.

At spread 0 every axis is `z`, so `R_A z = z`, `R_A - I` sends `z` to zero, and shifting `t_X` along `z` breaks no equation. With noise, 12 motions give 121 mm and 136 degrees of error at spread 0 and 4.9 mm and 1.3 degrees at 15.

![Arm spinning, two cameras](../assets/clip-example.mp4)

*The arm spins about its upright axis. A camera 0.1 m higher (ghost) sees the same motion.*

![Rotation first, then translation](../assets/diagram-handeye-solve.png)

*Red: with parallel axes, the turn and the shift along that axis stay free.*

![Error against axis spread](../assets/fig-handeye-spread.png)

*Median of 60 noisy runs. Left: one axis is useless. Right: the axes' second-to-first singular value ratio (near zero when parallel) warns before the robot moves.*

## Build It

```python
U, s, Vt = np.linalg.svd(alpha.T @ beta)       # alpha = log(R_A), beta = log(R_B)
R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
t = np.linalg.lstsq(M, y, rcond=None)[0]       # M stacks (R_A - I), y stacks R_X t_B - t_A
```

`make_motions()` builds `A`, then `B = X^-1 A X` plus noise. `solve_hand_eye()` also returns the singular values.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/04-hand-eye-calibration -q
```

## Use It

OpenCV's `cv2.calibrateHandEye` offers five methods and wants many more than 3 poses.

Sources: [OpenCV calibration module](https://docs.opencv.org/5.0/main_modules/calib.html) and [OpenCV 3.4.20 calib3d reference](https://docs.opencv.org/3.4.20/d9/d0c/group__calib3d.html), found by search 2026-11-09 (fetch returned HTTP 403).

## Ship It

`outputs/skill-hand-eye-check.md` checks motions for axis diversity before the robot runs them.

## Exercises

1. Add noise only to translations.
2. Replace the SVD with an average of rotations.
3. Plot error against motion count at 60 degrees of spread.
