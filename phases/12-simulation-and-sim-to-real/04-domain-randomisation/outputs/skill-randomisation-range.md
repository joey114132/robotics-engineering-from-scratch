---
name: randomisation-range
description: Use when choosing how wide to randomise simulator parameters (mass, friction, lag, delay) before tuning or testing a controller for a real robot, or when gains that work in simulation fail on hardware. Sets the range from measured uncertainty and checks its cost.
---

# Randomisation range

1. Get the real uncertainty first: identification error bars (lesson 12/03), datasheet tolerances, measured spread between units. Set the width from that, not from a guess.
2. Fix the controller family and a written success test (settle time, overshoot, limits). Count a failure as a cost, not as a missing sample.
3. Evaluate nominal-tuned gains on plants drawn at the real width. A big drop in success means the gains sit on a cliff edge.
4. Tune across a range equal to the real width and across two or three wider ones. Plot cost on the real-width plants against tuning width.
5. Pick the narrowest width whose success is acceptable. A much wider range costs speed on the plants that actually occur.
6. Check the batch simulator: one plant alone must equal the same plant in a batch.

Return the success-versus-width table, the chosen width with its measured cost and the parameters that mattered most. Never claim robustness beyond the widths you tested.
