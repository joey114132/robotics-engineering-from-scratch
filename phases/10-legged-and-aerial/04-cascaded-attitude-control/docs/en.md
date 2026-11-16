# Cascaded Attitude Control

> Learn how a drone stays level against steady wind, with a controller that remembers.

**Type:** Build   **Prerequisites:** 10/03 Quadrotor Model   **Time:** ~15 minutes

## In Plain Words

A steady gust leans on a drone's nose; it must fight back. A simple controller pushes back in proportion to the tilt, so the drone must stay tilted to push as hard as the gust.

Cascaded attitude control adds a memory. While the drone is not level, the memory adds a little more push until it matches the gust. Then the drone is level again and still resisting.

## Key Terms

- **Attitude**: how the drone is tilted in space.
- **PD control**: pushing back in proportion to the error (`kp`) and to how fast it changes (`kd`).
- **Cascade**: two loops, an angle loop outside that commands a turning speed to a rate loop inside.
- **Integral**: a running total of the error; it keeps growing while any error remains.
- **Gain**: the factor that turns an error into a push.
- **Stable**: a disturbance dies out instead of growing.

## The Problem

Picture a hovering drone pushed by a gust for a second. A simple controller holds a constant tilt for the whole gust, so the drone drifts. Raising `kp` shrinks the tilt but demands more torque.

## The Concept

A real drone fights wind all day, so it must resist the push and still stay level.

![PD](../assets/diagram-single-pd.png)

*Gust torque `d` leaves the error at `d / kp`.*

The outer loop turns angle error `e` into a turn-rate command `omega_ref = k_theta * e`; the inner loop turns rate error into torque. With P inside, `tau = k_w (k_theta e - omega)`: exactly PD with `kp = k_w k_theta` and `kd = k_w`.

![Cascade](../assets/diagram-cascade.png)

*Add an integral (gain `k_i`) of the rate error; it stops growing only at zero error, so it ends equal to the gust.*

Stable needs every root of `I s^3 + k_w s^2 + (k_w k_theta + k_i) s + k_i k_theta = 0` to have a negative real part.

With `I = 0.004`, `kp = 0.9`, `kd = 0.084`, `k_i = 0.5`, a 0.1 Nm gust holds the PD loop at `0.1 / 0.9 = 0.11 rad` (6.4 degrees). The cascade bumps to about 4 degrees, then pushes back 0.1 Nm at 0.5 degrees by 0.5 s.

![Push back](../assets/clip-example.mp4)

*Amber: push back. Red: gust. Both push back 0.1 Nm; only blue (PD) stays tilted.*

![Gust response](../assets/fig-gust-response.png)

*PD sits at 6.4 degrees. The cascade peaks near 4 degrees, returns near zero, then swings the other way when the gust stops.*

## Build It

```python
def cascade(k_theta, k_w, k_i):
    z = [0.0]
    def ctrl(ref, th, w, dt):
        e_w = k_theta * (ref - th) - w
        z[0] += e_w * dt
        return k_w * e_w + k_i * z[0]
    return ctrl
```

With `k_i = 0` this is a P-P cascade and equals `pd(kp, kd)`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/04-cascaded-attitude-control -q
python3 phases/10-legged-and-aerial/04-cascaded-attitude-control/code/main.py
```

## Use It

The last test checks `cascade_poles()` against SciPy's `TransferFunction`.

## Ship It

`outputs/skill-cascade-loop-check.md` reviews an attitude cascade for its integral and windup limits.

## Exercises

1. Raise `k_i` to 2; compare the post-gust swing with `k_i = 0.5`.
2. Clamp torque at 0.15 Nm; watch the integral.
3. Show that `k_w = 0.02` with `k_i = 2` is unstable.
