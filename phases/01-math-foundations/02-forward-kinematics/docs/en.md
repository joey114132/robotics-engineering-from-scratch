# Forward Kinematics

> Walk the chain: rotate about the joint, step along the link, repeat.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3)   **Time:** ~15 minutes

## In Plain Words

Join paper strips with drawing pins to make a flat arm on your desk. Turn the first strip and every strip
after it swings around too. Turn a later strip at its pin and only the strips beyond that pin change
direction.

Forward kinematics follows those turns from the base to the tip. Each link's direction includes the earlier
joint angles, so you add its length along that accumulated direction. Adding the resulting steps tells you
where the tip lands.

## The Problem

The controller knows joint angles, but the task lives in Cartesian space: put the gripper at (0.5, 0.3). Forward kinematics (FK) maps joint angles to the tip pose. Inverse kinematics, Jacobians and collision checks all sit on top of it, so an FK bug looks like a controller bug.

## The Concept

![Rotate then step, joint by joint](../assets/diagram-fk-walk.png)

*Each joint contributes `Rz(q)` and each link contributes `Tx(l)`. The tip pose is their ordered product.*

For a planar chain the same answer needs only cumulative angles, which gives an independent cross-check. The tip distance from the base is at most the sum of the lengths and at least `max(0, 2*longest - sum)`.

![When can the tip return to the base](../assets/diagram-reach-bounds.png)

*If the longest link is longer than all the others together, the workspace has a hole in the middle.*

![Random poses fill the predicted region](../assets/fig-workspace.png)

*3,000 random poses per arm. Left: links [1, 1] cover a full disc. Right: links [3, 1] never come closer than 2 m.*

## Build It

```python
def fk_planar(lengths, angles):
    heading = np.cumsum(angles)
    return np.sum(lengths*np.cos(heading)), np.sum(lengths*np.sin(heading)), heading[-1]

def fk_chain(angles, lengths):
    T = np.eye(4)
    for q, l in zip(angles, lengths):
        T = T @ _rz(q) @ _tx(l)
    return T
```

A test runs both on random poses and requires agreement to 1e-12.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/02-forward-kinematics -q
```

## Use It

Real arms use Denavit-Hartenberg parameters or URDF joint origins, and the axes are not all `z`. The structure is the same: one fixed transform and one joint transform per link. Before trusting any FK, read each URDF `<origin>` and ask which frame it is expressed in.

Sources: Craig, *Introduction to Robotics*, 3rd ed., ch. 3 (manipulator kinematics).

## Ship It

`outputs/skill-fk-check.md` is a two-implementation cross-check for any FK code.

## Exercises

1. Make joint 2 rotate about `y` and see why the planar test now fails.
2. Plot minimum reach against the length ratio of a two-link arm.
3. Find a pose of links [1, 1] where the tip returns to the base.
