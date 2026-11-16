# Frames and Transform Trees

> Learn a naming habit that stops you mixing up which part's view a position is measured from.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3)   **Time:** ~15 minutes

## In Plain Words

A camera on a mast reports a cup's position measured from the camera. The arm needs it from its own base, and the camera faces away, so the raw numbers mislead.

A transform tree stores how each frame (x, y, z directions attached to a part) sits in its parent. To convert the cup's position, multiply the transforms along the chain.

## Key Terms

- **Frame**: a set of x, y, z directions attached to a part, such as the camera or the base.
- **Transform tree**: a map where each frame hangs off exactly one parent frame.
- **`T_to_from`**: a transform that converts coordinates from the `from` frame into the `to` frame.
- **Common ancestor**: the nearest frame above two frames on the tree, where their paths meet.
- **Cycle**: a loop in which a frame becomes its own ancestor.
- **tf2**: the ROS 2 library that stores a transform tree.

## The Problem

A camera sees a cup, and the arm needs its position from its own base. Someone writes `T_cam_cup @ T_base_cam`, or inverts the wrong matrix, because the names carry no direction. Both are valid poses in the wrong place.

## The Concept

Each part of a robot sees the world from its own spot, so every reading must be converted.

`T_to_from` converts coordinates from `from` into `to`. In a product the inner names cancel: `T_a_b @ T_b_c = T_a_c`.

![A tree with one parent per frame](../assets/diagram-tf-tree.png)

*Each arrow stores `T_parent_child`. The camera and the hand both hang off the base.*

To get the cup as the hand sees it, climb from both frames to a shared ancestor, then go down one side with an inverse.

![Lookup climbs to the common ancestor](../assets/diagram-tf-lookup.png)

*To get `T_tool_cup`, climb to `base`, then use `inv(T_base_tool) @ T_base_cup`.*

The camera sits at (0.5, 0, 0.4) in the base frame, turned around, and sees the cup at (0.2, 0, 0.5), so in the base frame the cup is at (0.3, 0, 0.9). A hand at (0.3, 0, 0.7) sees it at (0, 0, 0.2).

![One cup measured from the camera, the base and the hand](../assets/clip-example.mp4)

*Dark blue arrow from the camera, green from the base, amber from the hand.*

![Cost of a wrong product](../assets/fig-wrong-order-error.png)

*Here a swapped product is off by up to 0.4 m, a stray inverse by up to 1.3 m.*

## Build It

```python
def lookup(self, to, frm):
    up_to, up_from = self._up(to), self._up(frm)
    common = next((f for f in up_from if f in up_to), None)
    if common is None:
        raise ValueError(f"{to} and {frm} are in different trees")
    return invert_T(self._to_ancestor(to, common)) @ self._to_ancestor(frm, common)
```

`add()` rejects a second parent and any cycle. `_to_ancestor()` multiplies stored transforms on the way up.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/04-frames-and-transform-trees -q
```

## Use It

ROS 2 `tf2` keeps the same structure, and `lookup_transform(target, source, time)` takes the target first. Compare it with `TFTree.lookup`.

Sources: signature checked in `tf2_ros/buffer.py` of the local ROS 2 Jazzy install.

## Ship It

`outputs/skill-frame-naming-review.md` audits transform products and frame names.

## Exercises

1. Add a `static_cam_cup` frame under `cam` and check the chain still cancels.
2. Make `lookup` return the frames it visited.
3. Say what interpolation `lookup` needs if edges carry a `time`.
