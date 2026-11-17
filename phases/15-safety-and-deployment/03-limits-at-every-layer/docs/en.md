# Limits at Every Layer

> Learn why a robot can quietly move slower than you asked, and how to catch it at startup.

**Type:** Build   **Prerequisites:** none   **Time:** ~15 minutes

## In Plain Words

A bench arm takes orders through three layers: the planner draws the path, the controller pushes the motor, and the drive is the motor's own electronics. Each has a speed limit.

If the planner allows twice the drive's speed, the plan runs ahead of the real arm and nothing reports it. The tightest limit wins.

## Key Terms

- **Planner**: the layer that draws the path and sets the speed it asks for.
- **Controller**: the layer that turns the path into motor commands.
- **Drive**: the motor's own electronics, which enforce its hard limits.
- **Clamp**: cut a value so it stays within a limit.
- **Effective limit**: the limit the joint really feels, set by the tightest layer.
- **Nested limits**: each layer allows a little less than the next, so the planner is the strictest.

## The Problem

You raise the speed limit in the planning software to 3 rad/s, but the arm still crawls at half that, with no error. A lower limit in the motor's electronics quietly cut the speed.

## The Concept

A robot has several layers that each set limits, so a mismatch hides. Each layer should be a little stricter than the next, so the planner is the strictest and the drive the loosest. If an early layer allows more than a later one, the later one quietly wins. A startup check can compare every pair before the robot moves.

![Nested limits](../assets/diagram-limits-nested.png)

*Healthy: each layer is a little stricter than the next.*

![Silent mismatch](../assets/diagram-limits-silent.png)

*The planner asks for a lot, the drive allows less.*

![Arm stops short](../assets/clip-example.mp4)

*The dark ghost is where the planner thinks the joint is. Blue stops short. Green's limits agree.*

![Limit stack](../assets/fig-limit-stack.png)

*Blue steps up from layer to layer. Orange breaks the pattern.*

![Limit lag](../assets/fig-limit-lag.png)

*With matching limits the joint keeps up. With mismatched limits it falls far behind the plan.*

<details><summary>The math (optional)</summary>

Healthy speed limits are 1.0, 1.5 and 2.0. In the mismatched case the planner and controller allow 3.0 but the drive only 1.5, so `effective(L, 'vel')` returns `(1.5, 'drive')`. For position, limits planner 2.2, controller 1.8 and drive 2.0 (the `MISMATCHED` values): a request for 2.0 rad is clamped by the controller to 1.8, so the joint stops at 1.80 rad and `effective(MISMATCHED, "pos")` returns `(1.8, 'controller')`, 0.2 rad short. With aligned limits the joint trails by 0.12 rad. With mismatched limits the planner finishes at 0.47 s while the joint is still 0.82 rad behind.

</details>

## Build It

Each layer is a small table of limits, `None` meaning no limit. The check compares neighbours.

```python
for (a, x), (b, y) in zip(set_, set_[1:]):
    if x > y:
        out.append((q, a, b, x, y, f"{a}.{q} = {x} is looser than {b}.{q} = {y}: {b} wins silently"))
```

`require_nested()` reports every mismatch at once. `effective()` returns the limit the joint really feels and its layer.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/03-limits-at-every-layer -q
python3 phases/15-safety-and-deployment/03-limits-at-every-layer/code/main.py
```

## Use It

Real stacks keep limits in the robot's description file (URDF), a controller config and the drive's own settings. Load all three into one table at startup.

## Ship It

`outputs/skill-limit-stack-audit.md` builds that table and reads the report.

## Exercises

1. Add a limit on how hard the motor may push (torque) to the check.
2. Add an acceleration limit to every layer.
3. Why does the check allow equal limits?
