---
name: motor-gearbox-check
description: Use when sizing or sanity-checking a geared joint motor, or when a drive tuned on an empty arm is assumed to hold under load. Computes stall torque, no-load speed, reflected inertia and how visible the load is to the motor.
---

# Motor and gearbox check

1. Collect `kt` (Nm/A), terminal resistance `R`, supply `V`, rotor inertia `J_r`, gear ratio `N`, and the output-side load inertia `J_L`. Mark any value that is a guess.
2. Stall torque is `kt*V/R`, no-load speed is `V/kt`. At the output multiply torque by `N` and divide speed by `N`. Use continuous limits from the datasheet for sustained work, not stall.
3. Load visibility is `(J_r + J_L/N^2) / J_r`. Near 1.0 the motor-side response will not change when the load changes: say so, and do not use motor-side signals alone to detect the load.
4. Time constant on the motor shaft is `(J_r + J_L/N^2) * R / kt^2`.

Return the five numbers, the visibility ratio and its meaning. Never write a command to a real drive.
