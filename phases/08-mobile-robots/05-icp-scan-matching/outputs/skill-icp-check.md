---
name: icp-check
description: Use when a scan-matching or point-cloud registration result looks wrong, jumps between frames, or when adding ICP to a mapping pipeline. Checks the initial guess, the geometry and the residual.
---

# ICP check

1. Record the initial guess (odometry or previous match) and its size in metres and degrees. Compare the translation with the point spacing and the rotation with the room's size. A start beyond what the structure can pull back is a local-minimum risk.
2. Check the geometry: if the scene is one straight wall or a long corridor, the slide along it is unobservable. Report the unobserved direction instead of the fitted shift.
3. Read the final rms nearest-point error. On this lesson's demo, the residual floor is about the point spacing, not a universal lower bound. Sampling, noise and geometry can bias the pose; even a tiny residual can accompany a wrong alignment.
4. Re-run from 5 perturbed starts. If the answers disagree by more than the spacing, the match is not trustworthy.

Return the start size, the unobserved directions, the residual against the spacing and the spread over restarts. Never accept a match on the residual alone.
