# Reading a URDF

> A URDF is a tree of links joined by joints, and every joint origin is written in its parent link's frame.

**Type:** Build   **Prerequisites:** 00/01 Python Env and numpy   **Time:** ~15 minutes

## The Problem

You read a robot description, add up the joint offsets to find where the hand sits, and the answer is far from what the viewer shows. The offsets were right. You read each one in the world frame, while the file writes it in the frame of the link before it.

## The Concept

![A URDF is a tree of links and joints](../assets/diagram-urdf-tree.png)

*Links are the nodes and joints are the edges. A link can have several children, but only one parent joint.*

Each joint has a parent, a child, an `<origin>` (a position `xyz` and a rotation `rpy`), and for a moving joint an axis and limits. The ROS wiki defines the origin as the transform from the parent link to the child link, and `rpy` as fixed-axis roll, then pitch, then yaw.

![Which frame is the origin written in?](../assets/diagram-origin-frame.png)

*The same `xyz` means two different places depending on the frame you read it in.*

![Shoulder yaw 90 degrees](../assets/fig-origin-frames.png)

*Top view. The shoulder origin turns the arm by 90 degrees, so the elbow offset points along y. A plain sum of offsets puts the hand 0.71 m away.*

## Build It

Parse with the standard library, then walk from the root to a tip, composing one 4x4 transform per joint.

```python
root = ET.fromstring(xml)
for e in root.findall("joint"):
    o = e.find("origin")
    joints[e.get("name")] = dict(parent=e.find("parent").get("link"),
                                 child=e.find("child").get("link"),
                                 xyz=_vec(o, "xyz"), rpy=_vec(o, "rpy"))
# T = T @ T_origin @ R_axis(q), for each joint on the chain
```

`chain()` follows parent links from the tip back to the root. `link_positions()` applies the origin first and the joint rotation second, and rejects a value outside the limits.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-setup-and-tooling/03-reading-a-urdf -q
```

## Use It

In a ROS 2 system, `robot_state_publisher` takes the URDF kinematic tree and the `joint_states` topic and publishes the resulting poses to tf2. Compare its transforms with `link_positions()` for the same joint values.

Sources: https://wiki.ros.org/urdf/XML/joint, https://github.com/ros/robot_state_publisher

## Ship It

`outputs/skill-urdf-reading-check.md` lists what to check when a URDF position looks wrong.

## Exercises

1. Add a prismatic joint and move a link along its axis.
2. Print every link that has more than one child.
3. Make the parser reject a tree with two roots.
