---
name: arm-dynamics-derivation-check
description: Use when a rigid-body arm model (M, Coriolis, torque) was derived by hand, generated, or adapted to a new arm, and you need confidence in it before computed-torque or gravity-compensation use.
---

# Arm dynamics derivation check

1. Build the model twice by independent roads: energy plus Lagrange, and a Newton-Euler recursion. Compare tau at 20 or more random (q, qd, qdd). They must agree to numeric precision.
2. Check M is symmetric and positive definite at those states.
3. Run free motion (tau = 0, no gravity) with RK4 for a second. Kinetic energy must stay constant. Drift points to a Coriolis sign or a missing term.
4. Add gravity as potential energy only after steps 1 to 3 pass.
5. If a reference engine is available, compare M entries and the bias force at the same states.

Return the maximum tau mismatch, the minimum eigenvalue of M, and the energy drift. Never edit the model; list the suspected term.
