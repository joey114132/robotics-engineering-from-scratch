---
name: urdf-reading-check
description: Use when a position computed from a URDF disagrees with a viewer, a simulator or a TF tree, or before trusting hand-written forward kinematics built from joint origins.
---

# URDF reading check

1. Build the tree: list each joint's parent, child and type. Confirm one root and one parent joint per link. Print the chain from root to the link in question.
2. Confirm every `<origin>` is treated as a transform from the parent link frame to the child frame, with `rpy` as fixed-axis roll, pitch, yaw. A plain sum of `xyz` values is wrong whenever any joint on the chain has a rotation.
3. Compose per joint: origin first, then the joint rotation about its axis. Check each joint value against its limits.
4. Compare the result with a second source (a viewer or the TF tree) at two or more joint settings, one of them all zeros.

Report the chain, the per-joint transforms, and the first joint where your result and the reference diverge. Do not edit the URDF.
