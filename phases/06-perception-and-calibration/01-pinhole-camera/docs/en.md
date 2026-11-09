# Pinhole Camera

> A pixel is a ray. Depth picks the point on it, so a depth error moves the point along the ray and the cost grows with distance.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3)   **Time:** ~15 minutes

## The Problem

A vision system reports a cup at pixel (520, 240) and the planner reaches for it. The gripper closes a few centimetres to the side. The pixel was on the cup rim, but the depth value came from the table behind it, so the 3D point slid along the viewing ray.

## The Concept

![Project to a pixel, unproject with depth](../assets/diagram-pinhole-pipeline.png)

*Projection divides by `z` and throws depth away. Unprojection needs a depth to get a point back.*

With focal lengths `fx, fy` in pixels and principal point `cx, cy`, `u = fx*x/z + cx` and `v = fy*y/z + cy`. A pixel error `du` moves the point sideways by `z*du/fx`. A depth error `dz` moves it along the ray, which is sideways by `dz*(u-cx)/fx` away from the image centre.

![Two ways to read the wrong depth](../assets/diagram-pinhole-failure.png)

*The same pixel gives a good target or a bad one depending on where its depth was sampled.*

![Error against distance and against pixel offset](../assets/fig-pinhole-error.png)

*Left: 0.5 px and 1% depth both give errors proportional to distance. Right: a depth 0.15 m too far costs more sideways error the further the pixel is from the centre.*

## Build It

```python
def project(P, fx, fy, cx, cy):
    return np.stack([fx*P[:,0]/P[:,2] + cx, fy*P[:,1]/P[:,2] + cy], axis=1)

def unproject(uv, z, fx, fy, cx, cy):
    return np.stack([(uv[:,0]-cx)*z/fx, (uv[:,1]-cy)*z/fy, z], axis=1)
```

`position_error()` unprojects a pixel twice, with and without `du` and `dz`, and returns the difference. `project()` raises for `z <= 0`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/01-pinhole-camera -q
```

## Use It

Compare `project` with `cv2.projectPoints` on the same points, with zero rotation, zero translation and no distortion. The test skips if OpenCV is missing.

Sources: the [OpenCV calibration tutorial](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html) (an older version) uses `cv2.projectPoints` to compute reprojection error.

## Ship It

`outputs/skill-pixel-depth-check.md` checks that a pixel and its depth belong to the same surface.

## Exercises

1. Add a lens distortion term and see how far the unprojected point moves at the image corner.
2. Sample depth at the median of a 5x5 window and find the edge pixel where it still fails.
3. Express the error budget for a target at 2 m with `fx = 600` in millimetres.
