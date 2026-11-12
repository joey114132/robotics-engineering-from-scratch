# Time Sync and Traces

> Two clocks that disagree by a few milliseconds put sensor data in the wrong order, and a trace with before and after states shows where a run first went wrong.

**Type:** Build   **Prerequisites:** 05/03 Control Loop Jitter   **Time:** ~15 minutes

## In Plain Words

Students record a ball relay on separate watches. A watch running ahead can make an earlier handoff appear
later. Correcting its offset restores the sequence; an exchange timed at both ends estimates that offset, with
unequal travel delays leaving error.

A robot has the same clock problem across computers. Its trace also needs the state before and after each
action. Comparing those records with the intended handoffs reveals the first missing action, unchanged state,
or wrong result.

## The Problem

A fusion filter gets camera and IMU samples from two computers and behaves as if the robot jerks backwards. Every sample is correct, but the camera clock runs 30 ms ahead, so the filter sees events in the wrong order. When the run later fails, nobody can tell which step first went wrong.

## The Concept

![Four timestamps](../assets/diagram-offset-exchange.png)

*A request and reply give four timestamps. Half of the sum of the two one-way differences is the offset.*

The formula is exact when the way out and the way back take equally long. With unequal delays the error is half the difference, and never more than half the round trip, so the exchange with the smallest round trip is the one to trust.

![Offset estimate and order errors](../assets/fig-time-sync.png)

*Left: the lowest-delay exchange of 8 has a much tighter error than a single one. Right: with sensors 10 ms apart, an offset above 10 ms reorders them, and removing a 1 ms-accurate estimate restores the order.*

![Trace reader](../assets/diagram-trace-reader.png)

*Each trace line holds the state before and after one step. The reader checks each intent in order and stops at the first record that does not match.*

## Build It

```python
def estimate(t0, t1, t2, t3):
    return ((t1 - t0) + (t2 - t3)) / 2, (t3 - t0) - (t2 - t1)
```

`order_errors()` sorts two sensor streams by stamp and counts slots that differ from the true order. `trace_line()` writes one JSON object per step with `pre` and `post`. `first_mismatch()` returns `not_executed`, `no_motion` or `wrong_motion` for the first intent that fails.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/04-time-sync-and-traces -q
```

## Use It

In practice the system clock is synchronised by a service such as NTP, and ROS 2 asks for synchronised system clocks across a network. Compare `estimate()` with the offset and delay definitions in the NTP specification.

Sources: RFC 5905 (https://datatracker.ietf.org/doc/html/rfc5905) and ROS 2 design article "Clock and Time" (https://design.ros2.org/articles/clock_and_time.html), both read 2026-11-09.

## Ship It

`outputs/skill-trace-first-mismatch.md` reads a trace and names the first step that did not do what it was meant to.

## Exercises

1. Make `first_mismatch()` also flag a step whose `pre` differs from the previous step's `post`.
2. Add a per-exchange `proc` time and show that `estimate()` ignores it.
3. Fit a drift rate from offsets measured a minute apart and predict the offset after an hour.
