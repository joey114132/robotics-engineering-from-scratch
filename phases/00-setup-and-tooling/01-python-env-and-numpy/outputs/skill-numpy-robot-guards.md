---
name: numpy-robot-guards
description: Use when reviewing or writing numpy code that handles joint angles, points, poses or trajectories, to find missing unit and shape guards before the code reaches a simulator or robot.
---

# numpy robot guards

1. List every function that receives angles, positions or trajectories. Note the unit (rad, deg, m) and the shape each expects.
2. Check that each input boundary calls a shape check and, for angles, a degrees check. Flag any `np.sin`, `np.cos` or `np.arctan2` fed from a sensor or a config value with no unit conversion in sight.
3. Flag `a - b` or `a * b` between arrays whose shapes differ, since broadcasting hides a missing transpose.
4. Check that tests compare against a hand-calculated value, not only that shapes match.

Report each finding as file:line, the missing guard, and the one-line fix. Do not change code.
