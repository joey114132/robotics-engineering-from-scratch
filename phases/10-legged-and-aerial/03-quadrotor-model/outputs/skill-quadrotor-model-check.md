---
name: quadrotor-model-check
description: Use when writing or reviewing a quadrotor dynamics model or a position and attitude controller, or when a drone loses height in turns or lags a position command. Checks hover thrust, tilt coupling and units.
---

# Quadrotor model check

1. List the state, the inputs (total thrust, torques) and the sign convention for pitch. A sign flip between the model and the controller is the commonest bug.
2. Check the hover thrust equals `m*g` and that the model gives zero acceleration there at level attitude.
3. Check the tilt coupling: sideways `T*sin(theta)/m`, vertical `T*cos(theta)/m - g`. A controller that tilts without raising thrust to `m*g/cos(theta)` will sink.
4. Check that position commands go through an attitude loop. Position cannot be commanded to the torque directly because there are four integrations in between.
5. Check units (kg, kg m^2, N, N m, rad) and the inertia about the correct axis.

Return the hover thrust, the tilt coupling check, the sign convention and any controller that skips the attitude loop. Never send commands.
