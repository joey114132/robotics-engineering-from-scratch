# Pinhole Camera

> Learn why a camera gives the direction of a cup but not its distance, and what that costs.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3)   **Time:** ~15 minutes

## In Plain Words

A camera sees a cup in front of a wall. The cup's rim and a spot on the wall lie on one line of sight, so they share a pixel. A pixel gives a direction, not a distance, so the wall's depth sends the arm past the cup.

## Key Terms

- **Pixel**: one dot of a camera image.
- **Depth (`z`)**: how far a point is in front of the camera.
- **Ray**: the line of sight through a pixel. Every point on it lands on that pixel.
- **Focal length (`fx, fy`)**: how strongly the lens zooms in, measured in pixels.
- **Principal point (`cx, cy`)**: the pixel where the camera's centre line lands.
- **Projection**: turning a 3D point into a pixel.

## The Problem

A camera sees a cup at pixel (520, 240), yet the gripper closes a few centimetres to the side. The depth came from the wall behind the rim.

## The Concept

To grab what it sees, a robot must turn each pixel into a 3D point, and that needs a distance.

![Project to a pixel, unproject with depth](../assets/diagram-pinhole-pipeline.png)

*Projection (left) divides by `z` and loses depth. Going back (right) needs a depth.*

The camera frame has `x` right, `y` down and `z` forward, so `u = fx*x/z + cx` and `v = fy*y/z + cy`.

A pixel error `du` moves the point sideways by `z*du/fx`, more the farther away it is. A depth error `dz` slides it along the ray, sideways by `dz*(u-cx)/fx`: nothing at the centre pixel, more at the edge.

Take pixel `(520, 240)`, `fx = 600`, `cx = 320`. At the rim's depth, 1.00 m, the point is 0.33 m right of the centre line. At the wall's depth, 1.15 m, it is 0.38 m: 5 cm off.

![Two cups, depth too large](../assets/clip-example.mp4)

*Same 0.15 m mistake for both cups. The edge cup's ball also slides 5 cm sideways.*

![Two ways to read the wrong depth](../assets/diagram-pinhole-failure.png)

*Where the depth is read decides which point the pixel gives.*

![Error against distance and offset](../assets/fig-pinhole-error.png)

*Left: 0.5 px and 1% depth errors grow with distance. Right: a 0.15 m depth error costs more at the edge.*

## Build It

```python
def project(P, fx, fy, cx, cy):
    return np.stack([fx*P[:,0]/P[:,2] + cx, fy*P[:,1]/P[:,2] + cy], axis=1)

def unproject(uv, z, fx, fy, cx, cy):
    return np.stack([(uv[:,0]-cx)*z/fx, (uv[:,1]-cy)*z/fy, z], axis=1)
```

`position_error()` unprojects a pixel with and without `du` and `dz` and returns the difference.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/01-pinhole-camera -q
```

## Use It

Compare `project` with `cv2.projectPoints` on the same points.

Sources: the [OpenCV calibration tutorial](https://opencv24-python-tutorials.readthedocs.io/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html) (an older version) uses `cv2.projectPoints` for reprojection error.

## Ship It

`outputs/skill-pixel-depth-check.md` checks that a pixel and its depth belong to the same surface.

## Exercises

1. Add a lens distortion term.
2. Sample depth at the median of a 5x5 window and find where it still fails.
3. Give the error budget in millimetres for a target at 2 m with `fx = 600`.
