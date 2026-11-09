---
name: plane-fit-check
description: Use when a table, floor or wall plane is fitted to depth data and then used to place or measure something, or when a fitted plane looks tilted. Checks outlier sensitivity of the fit.
---

# Plane fit check

1. Fit the plane twice: plain least squares on all points, and RANSAC with a threshold of a few times the depth noise. Compute the angle between the two normals.
2. If the angle is more than about 1 degree, outliers are pulling the least-squares plane. Use the RANSAC plane and report the inlier fraction.
3. Check the inlier fraction. Under 50% means the dominant surface is not the one you wanted.
4. Choose iterations with `log(1 - p) / log(1 - w^3)` for the expected inlier fraction `w`.
5. Fix the random seed so the result repeats.

Return the angle between the two normals, the inlier fraction, the threshold used and a pass or fail. Never delete points without saying which ones.
