# Watchdogs and Stops

> A watchdog is only safe if the joint can stop in the room left after the timeout runs out.

**Type:** Build   **Prerequisites:** 15/01 Failure Modes   **Time:** ~15 minutes

## In Plain Words

A bench arm swings toward its hard stop, the block that ends its travel, when the program steering it crashes. The joint keeps carrying out the last command. A watchdog expects a regular "still here" message, the heartbeat, and orders a stop when the silence outlasts its timeout.

The arm keeps moving during that timeout, and braking needs more distance, growing with the square of the speed. Cutting power is not braking. Like a bike you stop pedalling, the arm only coasts.

## The Problem

The program that sends commands crashes, and the joint keeps running its last velocity. The watchdog notices the silence, but its stop takes time and distance. Some stops are not stops at all.

## The Concept

![A heartbeat keeps the joint allowed to move](../assets/diagram-watchdog-flow.png)

*Follow the dashed heartbeat. If it goes quiet longer than the timeout, the watchdog hands the joint to a stop action.*

Braking at constant deceleration `a` (how fast the speed drops, in rad/s^2) from speed `v` takes `t = v / a` and covers `v * t - a * t^2 / 2 = v^2 / (2a)`. Before braking starts, the joint moves for the whole timeout `T`.

![The distance budget after the program dies](../assets/diagram-stop-budget.png)

*Travel during the timeout plus braking travel must fit in the room to the limit, which bounds T.*

Worked example. The joint is at 1.0 rad moving at 2 rad/s and the stop is at 1.5 rad, so the room is 0.5 rad. Braking at 8 rad/s^2 needs 2^2 / (2 * 8) = 0.25 rad, leaving 0.25 rad for the timeout: T <= 0.25 / 2 = 0.125 s. A 0.05 s timeout stops at 1.30 rad in simulation, under the formula's 1.35 (1.0 + 0.1 + 0.25) because friction helps. A 0.2 s timeout travels 0.4 rad first and hits the stop.

![Two bench arms brake after different watchdog timeouts](../assets/clip-example.mp4)

*Same braking, two timeouts; the lamp marks the trip. Green trips after 0.05 s and halts short. Blue waits 0.2 s and hits the stop.*

![Torque cut against a ramped stop](../assets/fig-cut-vs-ramp.png)

*Both stops start together. Switching the motor off leaves only friction, so the joint coasts through the limit. A ramped stop, steady braking, ends short.*

![Overrun against watchdog timeout](../assets/fig-timeout-budget.png)

*Each 10 ms of timeout adds 2 rad/s * 10 ms = 0.02 rad. The simulation sits just under the formula, a conservative bound.*

A timeout also has a lower bound: it must exceed the heartbeat period plus jitter (how much arrivals wobble), or one late message stops the joint for no reason.

## Build It

```python
def stop_distance(v, a):
    return v * v / (2.0 * a)

def max_timeout(room, v, a):
    return (room - stop_distance(v, a)) / v   # raises if this is <= 0
```

`simulate()` runs a joint holding 2 rad/s with a 1.5 rad limit, kills the command program at 0.5 s, and applies `"cut"` (zero torque) or `"ramp"` (brake at 8 rad/s^2).

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/02-watchdogs-and-stops -q
python3 phases/15-safety-and-deployment/02-watchdogs-and-stops/code/main.py
```

## Use It

A real drive has its own brake, safe deceleration and timeout: put the documented values into `max_timeout`. This joint has no brake, so cut means "no help from the drive".

## Ship It

`outputs/skill-watchdog-budget.md` checks a watchdog timeout against the stopping budget and heartbeat period.

## Exercises

1. Double the speed to 4 rad/s and show with `max_timeout` that 0.5 rad of room no longer works.
2. Lower the deceleration until `max_timeout` raises, and say what that means for the design.
3. Add 5 ms of heartbeat jitter and find the smallest timeout with no false trips.
