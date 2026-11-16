# Motor and Gearbox

> Learn why a gearbox makes a heavy load feel almost weightless to the motor.

**Type:** Build   **Prerequisites:** 03/02 Gravity Compensation   **Time:** ~15 minutes

## In Plain Words

A small motor spins a heavy flywheel through a gearbox. The flywheel turns far slower than the motor shaft, so the motor feels it as much lighter than it is.

A fast motor also pushes against itself with its own voltage, so its push fades as it speeds up.

## Key Terms

- **Torque**: a twisting push, the kind of force a motor puts on a shaft.
- **Back-EMF**: the voltage a spinning motor makes against its own supply, which cuts the current and the push.
- **Inertia**: how hard something is to spin up. A heavy flywheel has a lot.
- **Gear ratio (`N`)**: how many motor turns make one output turn. Torque grows `N` times and speed shrinks `N` times.
- **Stall torque**: the push a motor gives when held still, its strongest.
- **Drive**: the electronics that power and control the motor.

## The Problem

Your robot arm moves the same way before and after you hang a heavy tool on it. A 100:1 gearbox hides the load from the drive tuned on the empty arm.

## The Concept

This tells you how much motor a joint needs, and why one tuning keeps working when the load changes.

![Motor chain](../assets/diagram-motor-chain.png)

*More speed, more back-EMF, less torque.*

`V` is supply voltage, `w` shaft speed, `R` winding resistance and `kt` the torque constant (torque per amp). Current is `(V - kt*w) / R` and torque is `kt * current`. Torque falls on a line from the stall torque (at `w = 0`) to zero at `V / kt`.

![Reflected inertia](../assets/diagram-reflected-inertia.png)

*Inertia divided by N squared leaves the rotor in charge.*

A gearbox of ratio `N` multiplies torque by `N` and divides speed by `N`. Spinning energy grows with speed squared, so the motor feels the flywheel as only `J_L / N^2`.

Take rotor inertia `J_r = 2e-5` and flywheel inertia `J_L = 2e-3` (kg m^2). At `N = 1` the motor feels 101 times its own inertia and needs 0.81 s instead of 8 ms to reach 63% of final speed. At `N = 100` it feels 1.01 times and needs 8.08 ms.

![Two gear ratios](../assets/clip-example.mp4)

*Left (N = 1): the rotor creeps. Right (N = 100): it races.*

![Torque line and spin-up](../assets/fig-motor-gearbox.png)

*Left: the gearbox shifts the line. Right: at N = 100 loaded and bare curves coincide.*

## Build It

The load torque arrives divided by `N`.

```python
def motor_torque(w, kt, R, V):
    return kt * (V - kt * np.asarray(w, float)) / R

def load_at_motor(J_load, N):
    return J_load / N**2

def inertia_sensitivity(J_rotor, J_load, N):
    return (J_rotor + load_at_motor(J_load, N)) / J_rotor
```

`spin_up()` solves `J * dw/dt = motor_torque(w) - tau_load / N`. Sensitivity 1.0 means the drive cannot see the load.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/01-motor-and-gearbox -q
python3 phases/04-actuators-and-sensors/01-motor-and-gearbox/code/figure.py
```

## Use It

MuJoCo documents a DC motor actuator with these terms.

Sources: [MuJoCo DC motor model](https://mujoco.readthedocs.io/en/latest/_static/dcmotor.pdf), [Faulhaber DC motor calculations](https://www.faulhaber.com/en/know-how/tutorials/dc-motor-tutorial-motor-calculations-for-coreless-brush-dc-motors/); accessed 2026-11-09.

## Ship It

`outputs/skill-motor-gearbox-check.md` turns motor constants and a ratio into stall torque and load visibility.

## Exercises

1. Add friction `b*w` and find the new top speed.
2. Find the `N` at which the load adds only 5% to the motor-side inertia.
3. Add a gearbox efficiency below 1.
