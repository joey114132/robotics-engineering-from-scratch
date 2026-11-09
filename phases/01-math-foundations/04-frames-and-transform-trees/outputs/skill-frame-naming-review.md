---
name: frame-naming-review
description: Use when reviewing code that composes transforms between named frames (TF trees, hand-eye calibration, sensor-to-base chains, URDF-derived poses). Checks T_to_from naming, product order, inverse use and tree structure.
---

# Frame naming review

1. Every transform variable is named `T_<to>_<from>`. List each product and flag any whose inner names differ: `T_a_b @ T_b_c` is valid, `T_a_b @ T_c_b` is not.
2. For each inverse, confirm the swapped name matches what the call site needs. A stray inverse is the second most common source of a valid-but-wrong pose.
3. Check the tree: one parent per frame, no cycles, one root per connected group. A lookup between different trees must fail loudly.
4. Confirm that lookup APIs take the target frame first (`lookup(to, from)`), and state this order at each call site.
5. For each printed or published pose, name the frame it is expressed in and the frame it describes.

Return PASS or a list of `file:line` violations. Never edit.
