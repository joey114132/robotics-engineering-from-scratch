---
name: time-step-check
description: Use when a simulation or step-by-step loop moves something, to choose a time step and check that a smaller step does not change the answer much.
---

# Time step check

1. Find the step size (`dt`) and say how many steps one second needs.
2. Pick a case with a known true answer, such as a steady speed or a free fall, and compare.
3. Run again with half the step. If the answer moves a lot, the step is too big.
4. Check the order: the speed is updated first, then the position moves by the new speed.

Report the step size, the two answers and how far apart they are. Do not change code.
