# Frames and Transform Trees

> Name every transform `T_to_from`, and let the tree find the path between any two frames.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3)   **Time:** ~15 minutes

## In Plain Words

A camera on a mast sees a cup and reports its position measured from the camera. The arm needs that spot measured from its own base, and the camera faces the other way, so its numbers would aim the arm at the wrong place.

A transform tree stores how each frame (the x, y, z directions attached to a part) sits inside its parent, like the camera on the base. To convert the cup's position, multiply the transforms along the chain. Matching frame names show which ones fit together.

## The Problem

A camera sees a cup, and the base needs the cup's position. Someone writes `T_cam_cup @ T_base_cam`, or inverts the wrong matrix, because the names `cam` and `base` carry no direction. Both results are valid poses in the wrong place, and no error is raised.

## The Concept

`T_to_from` converts coordinates from `from` into `to`. In a product the inner names cancel: `T_a_b @ T_b_c = T_a_c`. If the inner names differ, the product is wrong.

![A tree with one parent per frame](../assets/diagram-tf-tree.png)

*Each arrow stores `T_parent_child`, which maps coordinates in the child into the parent. The camera and the hand both hang off the base.*

To get the cup as the hand sees it, climb from both frames to a shared ancestor, then go down one side with an inverse.

![Lookup climbs to the common ancestor](../assets/diagram-tf-lookup.png)

*Follow the numbers. To get `T_tool_cup`, climb from both frames to `base`, then use `inv(T_base_tool) @ T_base_cup`.*

Put the camera at (0.5, 0, 0.4) in the base frame, turned around, and the cup at (0.2, 0, 0.5) in the camera frame. Turned around, the camera's x points back toward the base, so in the base frame the cup is at (0.5 - 0.2, 0, 0.4 + 0.5) = (0.3, 0, 0.9). A hand at (0.3, 0, 0.7) sees it at (0, 0, 0.2): straight up, 0.2 away.

![One cup measured from the camera, the base and the hand](../assets/clip-example.mp4)

*Watch the three arrows: sky from the camera, grey from the base, amber from the hand. The arm follows the amber one, straight up.*

![Cost of a wrong product](../assets/fig-wrong-order-error.png)

*With the camera at (0.5, 0, 0.4) in the base frame and the cup at (0.2, 0, 0.5) in the camera frame, a swapped product is off by up to 0.4 m and a stray inverse by up to 1.3 m.*

## Build It

```python
def lookup(self, to, frm):
    up_to, up_from = self._up(to), self._up(frm)
    common = next((f for f in up_from if f in up_to), None)
    if common is None:
        raise ValueError(f"{to} and {frm} are in different trees")
    return invert_T(self._to_ancestor(to, common)) @ self._to_ancestor(frm, common)
```

`add()` rejects a second parent and any cycle (a frame that is its own ancestor). `_to_ancestor()` multiplies stored transforms on the way up.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/04-frames-and-transform-trees -q
```

## Use It

ROS 2 `tf2`, the transform library, keeps the same structure: one parent per frame, lookups through a common ancestor, and `lookup_transform(target, source, time)` taking the target first. Compare its result with `TFTree.lookup` on the same tree.

Sources: signature checked in `tf2_ros/buffer.py` of the local ROS 2 Jazzy install.

## Ship It

`outputs/skill-frame-naming-review.md` audits transform products and frame names in a code review.

## Exercises

1. Add a `static_cam_cup` frame under `cam` and check the chain still cancels.
2. Make `lookup` return the list of frames it visited.
3. Add `time` to each edge and say what interpolation `lookup` would need.
