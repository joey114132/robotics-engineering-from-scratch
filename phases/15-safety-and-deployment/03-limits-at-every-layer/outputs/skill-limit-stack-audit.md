---
name: limit-stack-audit
description: Use when a robot joint or axis is slower, weaker or shorter-ranged than a config says, or when position, velocity or torque limits are set in more than one place (planner, controller, drive, model file). Builds one table of limits per layer and finds the layer that wins silently.
---

# Limit stack audit

1. List every layer that clamps the command path, outermost first: planner or trajectory generator, controller, drive or firmware, and the model file if it carries limits.
2. For position, velocity, torque (and acceleration if present) record each layer's value and where it was read from. Read drive values from the drive, not from a config copy.
3. For each quantity compare neighbouring layers that both set it. Upstream must not be looser than downstream. Report every violation as `layer.quantity = x is looser than next.quantity = y: next wins silently`.
4. Report the effective limit per quantity and the layer that owns it.
5. Put the check at startup, before the first motion, and make it refuse to run on a mismatch unless a human overrides it.

Return the table, the violations and the effective limits. Do not change any value.
