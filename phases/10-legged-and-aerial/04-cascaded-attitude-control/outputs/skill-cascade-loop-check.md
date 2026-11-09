---
name: cascade-loop-check
description: Use when writing or reviewing an angle-over-rate attitude controller, or when a vehicle holds a steady tilt under wind or load. Checks that the rate loop has an integral, that the integral is limited, and that the loop bandwidths are ordered.
---

# Cascade loop check

1. Write the structure: outer angle loop gain, inner rate loop gains, plant inertia. Compute the equivalent single-loop gains `kp = k_w*k_theta`, `kd = k_w`. If the inner loop has no integral, the cascade is a PD loop and has an offset `d/kp` under a constant torque.
2. Check that the inner rate loop is faster than the outer. The rate-loop pole is `k_w/I` and the outer loop pole is about `k_theta`. Report both and the ratio.
3. Check the integral: a clamp, a reset on saturation, or a freeze while the output is saturated. Without one, a limited actuator winds the integral up.
4. Compute the closed-loop poles of `I s^3 + k_w s^2 + (k_w*k_theta + k_i) s + k_i*k_theta`. Any pole with a non-negative real part is a failure. A weak `k_w` with a large `k_i` can fail.
5. Check where the rate comes from. It should be the gyro, not a derivative of the angle.

Return the equivalent PD gains, the bandwidth ratio, the integral limit and the pole check. Never change gains or send commands.
