# Cascaded Attitude Control

> An angle loop outside a rate loop is the same as PD until you give the inner loop an integral, and then a gust stops costing you an angle error.

**Type:** Build   **Prerequisites:** 10/03 Quadrotor Model   **Time:** ~15 minutes

## The Problem

A gust pushes the drone for a second. Your PD pitch loop holds a constant tilt for the whole second. Pitch sets sideways speed, so the drone slides off its spot. Raising `kp` shrinks the tilt, but it also raises the torque the loop asks for on every small error.

## The Concept

![One loop: PD on the angle](../assets/diagram-single-pd.png)

*The single loop turns an angle error into torque. A steady gust torque `d` needs `kp * error = d`, so the error stays at `d / kp`.*

The cascade splits the job. The outer loop turns angle error into a rate command, `omega_ref = k_theta * error`. The inner loop turns rate error into torque. With a P inner loop, `tau = k_w (k_theta e - omega)`, which is exactly PD with `kp = k_w k_theta` and `kd = k_w`. A test confirms the two give identical trajectories.

![Two loops: angle outside, rate inside](../assets/diagram-cascade.png)

*Same outer gain, plus an integral on the rate error. The integral state grows until it cancels the gust, with no angle error needed.*

The integral gives the characteristic polynomial `I s^3 + k_w s^2 + (k_w k_theta + k_i) s + k_i k_theta`. For the gains here its roots are all in the left half plane.

![A one-second gust on both loops](../assets/fig-gust-response.png)

*The PD loop sits at 6.4 degrees for the whole gust. The cascade peaks at about 4 degrees and returns to zero before the gust ends. When the gust stops, the stored integral makes it swing about 4 degrees the other way.*

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

With `k_i = 0` this is a P-P cascade and equals `pd(kp, kd)`. The example uses `I = 0.004`, `kp = 0.9`, `kd = 0.084` (natural frequency 15 rad/s, damping 0.7) and `k_i = 0.5`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/04-cascaded-attitude-control -q
python3 phases/10-legged-and-aerial/04-cascaded-attitude-control/code/main.py
```

## Use It

SciPy's `TransferFunction` gives the same closed-loop poles as `cascade_poles()`, and the last test checks that. A real flight controller also filters the gyro and limits the integral so it cannot wind up.

## Ship It

`outputs/skill-cascade-loop-check.md` reviews an attitude cascade for rate-loop integral, windup limits and loop bandwidth ordering.

## Exercises

1. Raise `k_i` to 2 and compare the post-gust swing with `k_i = 0.5`.
2. Clamp the torque at 0.15 Nm and watch what the integral does.
3. Show that the same gain split with `k_w = 0.02` and `k_i = 2` is unstable.
