---
name: intrinsics-calibration-check
description: Use when a camera calibration result (fx, fy, cx, cy) is about to be trusted, or when unprojected points are off near the image edge. Checks view diversity, reprojection error and plausibility.
---

# Intrinsics calibration check

1. Count the views and the distinct target orientations. Fewer than 3 views, or views that only translate, make the problem degenerate.
2. Recompute the reprojection error on points that were not used for the fit. Compare it with the detector noise. A large multiple of the noise means too few or too similar views.
3. Check plausibility: `cx, cy` near the image centre, `fx` close to `fy`, `fx` close to the lens datasheet value. Large gaps point to a bad view, not a surprising camera.
4. Confirm the resolution of the images used. Intrinsics do not transfer to another resolution without scaling.

Return view count, orientation spread, held-out reprojection error and pass or fail. Never overwrite a stored calibration.
