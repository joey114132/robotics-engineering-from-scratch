# Depth and Point Clouds

> A depth image is a cloud waiting to be unprojected. Thin it with a voxel grid, then find the table with RANSAC because a plain least-squares plane believes every stray point.

**Type:** Build   **Prerequisites:** 06/01 Pinhole Camera   **Time:** ~15 minutes

## In Plain Words

A depth camera on a stand looks down at a table with a box on it. The arm needs the table's flat surface to set a block down level. A fit that believes every point gets pulled toward the box and a few stray readings, so its plane tilts and the block leans.

RANSAC instead tries planes through three random points and counts how many points lie close to each. The plane most points agree with is the table, and the box and stray readings stay outside it.

## The Problem

A depth image shows a table with a box, plus a few stray pixels. You fit a plane so the arm can place objects. The plane tilts a few degrees, so a "flat" place pose leans.

## The Concept

![From depth image to table plane](../assets/diagram-cloud-pipeline.png)

*Every pixel with a depth becomes a point, voxels thin the cloud, and RANSAC returns the plane and a mask (which points lie on it).*

Unproject each pixel with its depth as in lesson 01. A voxel grid then cuts space into small cubes and keeps one averaged point per cube, so the cloud shrinks and the plane stays.

A least-squares plane minimises the sum of squared distances, and squaring makes far points count far more, so a box 0.2 m closer than the table pulls it hard.

RANSAC picks three random points (three points define a plane), counts the points within a threshold (the inliers) and keeps the best plane. A round helps only if all three picks lie on the table, chance `w^3` for table share `w`. Drawing such a triple with chance `p` takes `N = log(1 - p) / log(1 - w^3)` rounds: `w = 0.88` and `p = 0.99` give `N = 5`, so 150 is a cheap margin.

Example, 1.2 cm threshold: a round drawing two box points and one table point gets only 1,142 of 19,200 points (one per depth pixel) within it, because the box top is 0.2 m above the table: the plane tilts 30 degrees. Three table points gave 16,836 (0.3 degrees off).

![Three RANSAC rounds](../assets/clip-example.mp4)

*Three rounds: amber balls are the picks, the sheet their plane, green points those within 1.2 cm. Only the last finds the table.*

![One RANSAC round](../assets/diagram-cloud-ransac.png)

*Each round: pick, plane, count; the winner is refit.*

![Least squares against RANSAC](../assets/fig-cloud-ransac.png)

*Left: least squares tilts toward the box and stray points; RANSAC follows the table. Right: the points off the plane are the box and the stray pixels.*

## Build It

```python
key = np.floor(P / size).astype(np.int64)
_, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
n = np.cross(b - a, c - a); n /= np.linalg.norm(n)
inl = np.abs((P - a) @ n) < thr
```

`voxel_downsample()` averages the points in each cell. `ransac_plane()` skips collinear samples and refits on the inliers. A 0.05 m voxel keeps under a fifth of the points and the same plane.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/06-perception-and-calibration/03-depth-and-point-clouds -q
```

## Use It

Open3D has `PointCloud.voxel_down_sample(voxel_size)` and `PointCloud.segment_plane(distance_threshold, ransac_n, num_iterations)`, which returns the plane coefficients and the inlier indices. Compare the plane normals.

Sources: [Open3D point cloud tutorial](https://www.open3d.org/docs/release/tutorial/geometry/pointcloud.html), checked for both function names and parameters.

## Ship It

`outputs/skill-plane-fit-check.md` checks how far stray points move a plane fit before it is used for placing.

## Exercises

1. Raise the stray-pixel rate (`flyers`) until the RANSAC plane at 150 iterations fails.
2. Use `ransac_iters` to choose the iteration count for 60% inliers.
3. Fit the box top as a second plane after removing the table inliers.
