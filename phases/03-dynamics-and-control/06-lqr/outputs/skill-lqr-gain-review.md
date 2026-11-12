---
name: lqr-gain-review
description: Use when someone proposes Q and R weights or an LQR gain K for a linear model, or tunes kp/kd on a state-space system by feel. Reviews the choice by closed-loop poles, cost and peak input.
---

# LQR gain review

1. Confirm the model (A, B) and the sample time. A gain computed for one dt is wrong for another.
2. Recompute K with a Riccati loop until P is steady. Report the closed-loop eigenvalue magnitudes; any at or above 1 is a failure.
3. Simulate from a realistic worst-case start. Report the peak input against the actuator limit and the settling time.
4. If the peak exceeds the limit, raise R and recompute. Do not clip a gain that was computed without the limit.
5. Compare the cost with the current hand-tuned gain on the same start.

Return K, pole magnitudes, peak input, settling time and the cost ratio. Never change gains on hardware.
