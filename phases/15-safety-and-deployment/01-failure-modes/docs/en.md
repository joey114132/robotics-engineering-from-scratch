# Failure Modes

> Before you can guard a joint you have to know how it breaks, and the worst faults are the quiet ones.

**Type:** Build   **Prerequisites:** 03/02 Gravity Compensation   **Time:** ~15 minutes

## The Problem

A joint that tracked well all week suddenly slams into its stop, and the log shows no error. The controller did exactly what its inputs told it to. This lesson injects five faults into a small PD loop, then measures how much damage each does and how soon a cheap check could have noticed.

## The Concept

![Where each fault enters the loop](../assets/diagram-fault-points.png)

*Wrong sign and saturation live in the command path. Stuck, dropout and delay corrupt what the controller believes about the joint.*

A fault is only dangerous through the loop it sits in. A stuck sensor makes the controller push on a joint it thinks is still. A wrong sign turns the spring into a repeller.

![Joint response under each fault](../assets/fig-fault-responses.png)

*Dashed gray is the healthy run. The blue vertical line is the first alarm. Wrong sign and stuck end pinned at the limit, dropout slams into it and recovers, delay rings, saturation crawls.*

![Damage and warning time](../assets/fig-fault-ranking.png)

*Left: error left at the end. Right: the alarm comes before the limit for every fault that reaches it, but saturation is only caught by a clock.*

![Which cheap check sees which fault](../assets/diagram-fault-checks.png)

*Four checks on the controller's own signals are enough to flag all five faults in this model.*

## Build It

`simulate(fault)` runs a 1-DOF joint (`J qdd = tau - b qd`) with a hard stop at 2 rad. Each fault is a few lines inside the loop, for example:

```python
if fault == "stuck" and on:
    held = held or (q, qd)
    qm, qdm = held          # controller sees a frozen joint
tau = clip(kp*(q_ref - qm) - kd*qdm, -tau_max, tau_max)
if fault == "wrong_sign":
    tau = -tau
```

`metrics()` measures the true joint. `alarm_time()` uses only what the controller can see. `ranked()` sorts by reached-limit, then final error, then speed.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/01-failure-modes -q
python3 phases/15-safety-and-deployment/01-failure-modes/code/main.py
```

```text
rank fault        peak|q| final err limit at alarm at  warned first
1    wrong_sign      2.00     3.000    0.460    0.205  True
2    stuck           2.00     3.000    1.301    0.350  True
3    dropout         2.00     0.000    0.513    0.300  True
4    delay           1.77     0.451    never    0.300  True
5    saturation      1.37     0.190    never    2.000  True
6    none            1.16     0.000    never    never  False
```

## Use It

The same injection works in a MuJoCo joint or a ROS 2 node. Wrap the sensor topic and the command topic, then compare your own monitors against this table. These thresholds belong to this plant, so re-measure them on yours.

## Ship It

`outputs/skill-fault-injection-review.md` lists the five faults to inject and the questions to ask about each monitor.

## Exercises

1. Inject the stuck sensor after the joint has settled and explain why nothing bad happens.
2. Find the delay in milliseconds at which this loop first rings.
3. Add a sixth fault, an encoder that reads twice the true angle, and rank it.
