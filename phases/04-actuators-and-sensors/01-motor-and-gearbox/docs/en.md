# Motor and Gearbox

> A motor is a torque source that weakens as it speeds up, and a gearbox makes the load almost invisible to it.

**Type:** Build   **Prerequisites:** 03/02 Gravity Compensation   **Time:** ~15 minutes

## In Plain Words

A bike's low gear makes the pedals turn farther for the same wheel movement. You need less pedal torque to
move the load, while the wheel turns more slowly for a given pedalling speed.

A motor gearbox makes that trade too. The load's inertia seen at the motor shrinks with the square of the
reduction ratio, so the rotor's own inertia can dominate. The DC motor in this model also loses torque as it
speeds up at fixed voltage, because back-EMF leaves less voltage to drive current.

## The Problem

You pick a motor for a joint, add a 100:1 gearbox, and the joint moves fast and strong. Then you tune the drive with the arm empty and it behaves the same when the arm holds a heavy tool. The drive has no idea what is on the end of the arm. The cause is two lines of algebra.

## The Concept

![Voltage to output torque](../assets/diagram-motor-chain.png)

*Voltage drives current, current makes torque, and the speed-dependent back-EMF takes some of the voltage back.*

Current is `(V - kt*w) / R` and torque is `kt * current`, so torque falls on a straight line from stall torque at `w = 0` to zero at the no-load speed `V / kt`. In SI units the torque constant and the back-EMF constant are the same number.

![Reflected inertia](../assets/diagram-reflected-inertia.png)

*Dividing the load inertia by N squared leaves the rotor inertia dominating.*

A gearbox of ratio `N` multiplies torque by `N` and divides speed by `N`. Kinetic energy goes with speed squared, so the load inertia seen at the motor is `J_L / N^2`.

![Torque-speed line and spin-up curves](../assets/fig-motor-gearbox.png)

*Left: the gearbox moves the line but does not bend it. Right: at N = 100 the speed response with and without the load is almost the same.*

## Build It

Motor-side dynamics with the load torque arriving divided by `N`.

```python
def motor_torque(w, kt, R, V):
    return kt * (V - kt * np.asarray(w, float)) / R

def load_at_motor(J_load, N):
    return J_load / N**2

def inertia_sensitivity(J_rotor, J_load, N):
    return (J_rotor + load_at_motor(J_load, N)) / J_rotor
```

`spin_up()` integrates `J * dw/dt = motor_torque(w) - tau_load / N`. A sensitivity near 1.0 means the drive cannot see the load.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/01-motor-and-gearbox -q
python3 phases/04-actuators-and-sensors/01-motor-and-gearbox/code/figure.py
```

## Use It

Simulators use the same model. MuJoCo documents a DC motor actuator with these terms, and a motor tutorial lists the torque constant and terminal resistance. Compare your `kt`, `R` and rotor inertia with a real datasheet before trusting a number.

Sources: [MuJoCo DC motor model](https://mujoco.readthedocs.io/en/latest/_static/dcmotor.pdf), [Faulhaber DC motor calculations](https://www.faulhaber.com/en/know-how/tutorials/dc-motor-tutorial-motor-calculations-for-coreless-brush-dc-motors/), accessed 2026-11-09.

## Ship It

`outputs/skill-motor-gearbox-check.md` turns motor constants and a ratio into stall torque, no-load speed and load visibility.

## Exercises

1. Add viscous friction `b*w` and find the new terminal speed.
2. Find the ratio `N` at which the load adds only 5% to the motor-side inertia.
3. Add a gearbox efficiency below 1 and show it lowers output torque but not the speed.
