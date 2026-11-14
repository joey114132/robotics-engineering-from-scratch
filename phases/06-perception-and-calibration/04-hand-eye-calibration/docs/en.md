# Hand-Eye Calibration

> A camera bolted to a gripper gives two views of every motion. `A X = X B` finds where the camera sits, but only if the robot rotates about more than one axis.

**Type:** Build   **Prerequisites:** 01/04 Frames and Transform Trees, 06/01 Pinhole Camera   **Time:** ~15 minutes

## In Plain Words

A camera is bolted to a robot arm's hand, and the arm must pick up a cup the camera sees. The camera reports the cup in its own view, so the arm must know where the camera sits on the hand, called X.

To find X, move the arm and compare how the hand moved with how the camera saw it. If every motion spins about one axis, a camera slid along that axis would report the same motions, so its position along it stays unknown. Different axes fix that.

## The Problem

The camera sees a cup 0.4 m ahead and the gripper must go there. Without `X`, the camera-to-gripper transform, it lands off by exactly the unknown offset. Calibrating with motions that all spin about one axis looks fine and is wrong.

## The Concept

![Why the equation is AX = XB](../assets/diagram-handeye-setup.png)

*Each motion is measured twice: `A` from the joints and `B` from the camera. `X` never changes, so `A X = X B` holds.*

Each motion is a rotation `R` plus a translation `t`. Multiplying out `A X = X B` gives two parts. Rotation: `R_A R_X = R_X R_B`, so `R_A` is `R_B` seen through `R_X`: same angle, axis turned by `R_X`, so `log(R_A) = R_X log(R_B)` (`log(R)` is axis times angle). An SVD lines up the axes to get `R_X`. Translation: `R_A t_X + t_A = R_X t_B + t_X`, so `(R_A - I) t_X = R_X t_B - t_A`, linear in `t_X`.

Example: the motions' axes lie in a cone around `z` whose half-angle is the spread. At spread 0 every axis is `z`, so `R_A z = z`, `R_A - I` sends `z` to zero, and shifting `t_X` along `z` breaks no equation. With noise, 12 motions give 121 mm and 136 degrees of error at spread 0 and 4.9 mm and 1.3 degrees at 15.

![Arm spinning with two cameras, one 0.1 m higher](../assets/clip-example.mp4)

*The arm spins about its upright axis. A camera 0.1 m higher on it (ghost) draws the same circle, so the motions cannot tell them apart.*

![Rotation first, then translation](../assets/diagram-handeye-solve.png)

*Red: when all axes are parallel, the turn about that axis and the shift along it stay free.*

![Error against axis spread](../assets/fig-handeye-spread.png)

*Median of 60 noisy runs. Left: one axis is useless, a few degrees of spread helps. Right: the axes' second-to-first singular value ratio (near zero when they point almost the same way) is known from the planned motions, so it warns before the robot moves.*

## Build It

```python
U, s, Vt = np.linalg.svd(alpha.T @ beta)       # alpha = log(R_A), beta = log(R_B)
R = U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
t = np.linalg.lstsq(M, y, rcond=None)[0]       # M stacks (R_A - I), y stacks R_X t_B - t_A
```

`make_motions()` builds `A`, then `B = X^-1 A X` plus noise. `solve_hand_eye()` also returns the singular values `s`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/04-hand-eye-calibration -q
```

## Use It

OpenCV's `cv2.calibrateHandEye(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam, method=...)` offers five methods and recommends many more than 3 poses. The test checks its rotation against the true `X`.

Sources: [OpenCV calibration module](https://docs.opencv.org/5.0/main_modules/calib.html) and [OpenCV 3.4.20 calib3d reference](https://docs.opencv.org/3.4.20/d9/d0c/group__calib3d.html), from search results on 2026-11-09; the pages returned HTTP 403 to fetch.

## Ship It

`outputs/skill-hand-eye-check.md` checks calibration motions for axis diversity before a robot runs them.

## Exercises

1. Add noise only to the translations: which part of `X` suffers?
2. Replace the SVD step with an average of axis-pair rotations and compare.
3. Plot error against the number of motions at 60 degrees of spread.
