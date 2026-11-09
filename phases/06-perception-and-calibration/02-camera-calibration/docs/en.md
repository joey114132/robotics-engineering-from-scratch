# Camera Calibration

> A flat grid seen from a few tilted views is enough to solve for `fx, fy, cx, cy` with linear algebra alone, but the answer is only as good as the views.

**Type:** Build   **Prerequisites:** 06/01 Pinhole Camera   **Time:** ~15 minutes

## The Problem

You trust the focal length printed in a datasheet, unproject a pixel at the image edge, and the point is a few centimetres off. The real `fx` and `cx` differ from the nominal values, and nothing in the image tells you so. You need to measure them from a target whose geometry you know.

## The Concept

![Four linear steps from grid to intrinsics](../assets/diagram-calib-steps.png)

*Each view of a flat grid gives a homography. Its columns constrain `B = K^-T K^-1`, and `K` falls out of `B`.*

For a plane at `Z = 0` the pixel is `K [r1 r2 t]` applied to `(X, Y, 1)`, so each view gives a 3x3 homography `H = K [r1 r2 t]`. Because `r1` and `r2` are orthonormal, `h1' B h2 = 0` and `h1' B h1 = h2' B h2`. Two linear equations per view, and `B` has five unknowns when skew is zero.

![Which views work](../assets/diagram-calib-views.png)

*Views that only slide the target sideways repeat the same constraints, so the solver rejects them.*

![Error against pixel noise](../assets/fig-calib-noise.png)

*Median over 100 seeded runs. The linear answer is several times the pixel noise with 3 views, and more views cut it by about half.*

## Build It

```python
A = np.array([r for H in Hs for r in (_v(H, 0, 1), _v(H, 0, 0) - _v(H, 1, 1))])
b = np.linalg.svd(A)[2][-1]          # smallest singular vector = [B11, B22, B13, B23, B33]
cx, cy = -B13 / B11, -B23 / B22
fx, fy = np.sqrt(lam / B11), np.sqrt(lam / B22)   # lam = B33 - B13^2/B11 - B23^2/B22
```

`homography_dlt()` normalises both point sets, stacks two rows per point and takes the smallest singular vector. `calibrate()` raises for degenerate or unphysical results.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/02-camera-calibration -q
```

## Use It

Run `cv2.calibrateCamera` on the same synthetic views with distortion terms fixed, and compare `fx` and `cy`. Production tools then refine the linear answer by minimising reprojection error with nonlinear least squares.

Sources: the [OpenCV calibration tutorial](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html) (an older version) describes `cv2.calibrateCamera` returning the camera matrix, distortion coefficients and poses, and uses reprojection error to check them.

## Ship It

`outputs/skill-intrinsics-calibration-check.md` reviews a calibration run: view diversity, error size and plausibility.

## Exercises

1. Remove the zero-skew assumption by adding `B12` and see how the error changes.
2. Find the smallest number of views that never fails at 1 px noise.
3. Add a nonlinear refinement step with `scipy.optimize.least_squares` and compare the error.
