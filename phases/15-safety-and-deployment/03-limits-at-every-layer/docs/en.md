# Limits at Every Layer

> When two layers disagree about a limit, the tighter one wins and nothing reports it.

**Type:** Build   **Prerequisites:** 15/02 Watchdogs and Stops   **Time:** ~15 minutes

## The Problem

You raise the speed limit in the planner to 3 rad/s and the joint still crawls at half that. Nothing logged a clamp, because the drive quietly cut the speed. Position, velocity and torque are each clamped by the planner, the controller and the drive, and no one checks that the three sets agree.

## The Concept

![Healthy: each layer is looser than the one before](../assets/diagram-limits-nested.png)

*The planner stays inside what the controller allows, and the controller inside what the drive allows. The outer layers are safety nets.*

The rule is simple. For each quantity, walk the layers from planner to drive and require every limit to be no looser than the next one that sets the same quantity. A violation means the downstream layer wins.

![Mismatch: the tightest layer wins and nobody says so](../assets/diagram-limits-silent.png)

*The planner asks for 3.0 and the controller agrees, but the drive allows 1.5. A startup check compares every pair and reports before the first move.*

![Limits per layer in two setups](../assets/fig-limit-stack.png)

*Blue steps up from layer to layer. Orange breaks the pattern for speed, torque and position.*

![Reference and joint in both setups](../assets/fig-limit-lag.png)

*Same goal, same gains. With aligned limits the joint trails by 0.12 rad. With mismatched limits the planner finishes at 0.47 s while the joint is still 0.82 rad behind.*

## Build It

Each layer is a small dict, `None` meaning the layer sets no limit. The check skips `None` and compares neighbours.

```python
for (a, x), (b, y) in zip(set_, set_[1:]):
    if x > y:
        out.append((q, a, b, x, y, f"{a}.{q} = {x} is looser than {b}.{q} = {y}: {b} wins silently"))
```

`require_nested()` raises once with every message. `effective()` returns the limit the joint really feels and the layer that owns it. `simulate()` runs the three clamps around a PD loop.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/03-limits-at-every-layer -q
python3 phases/15-safety-and-deployment/03-limits-at-every-layer/code/main.py
```

## Use It

Real stacks keep limits in a URDF, a controller config and the drive's own parameters. Load all three into one table at startup and run the same pairwise check. Where a source is a drive register, read it from the drive instead of trusting a copy.

## Ship It

`outputs/skill-limit-stack-audit.md` is a checklist for building that table and reading the report.

## Exercises

1. Make the planner torque limit explicit and extend the check to it.
2. Add an acceleration limit to every layer and report the effective one.
3. Explain why the check allows equal limits, and when you would want a margin instead.
