---
name: pixel-depth-check
description: Use when a target computed from a pixel and a depth value is off by centimetres, or before trusting a depth-camera point near an object edge. Checks that the pixel and the depth describe the same surface.
---

# Pixel and depth check

1. Write down `fx, fy, cx, cy` and the image size the pixel came from. Intrinsics from a different resolution are wrong until scaled.
2. Sample the depth in a small window around the pixel. If the min and max differ by more than the object's thickness, the pixel is on an edge and the depth may belong to the background.
3. Compute the sideways shift `dz * (u - cx) / fx` for the largest plausible `dz`. Compare it with the gripper clearance.
4. Prefer a pixel in the object's interior, or take the nearer of the window's depth modes.

Return the window depth spread, the worst-case sideways shift in millimetres, and a pass or fail. Never change the camera calibration.
