# Time Sync and Traces

> Learn how to line up two clocks, and how a step-by-step log shows where a run first went wrong.

**Type:** Build   **Prerequisites:** none   **Time:** ~15 minutes

## In Plain Words

A car has an IMU (a motion sensor) and a camera on separate computers. Software that merges their readings trusts each time stamp, so a clock running ahead puts events in the wrong order.

## Key Terms

- **Time stamp**: the time written on a reading by the clock of the computer that took it.
- **Clock offset**: how far one computer's clock runs ahead of another's.
- **Round trip**: the time a request takes to go out plus its reply to come back.
- **Sensor fusion**: merging readings from several sensors into one estimate.
- **Trace**: a log with one record per step, holding the state before and after.
- **Intent**: what a step is supposed to achieve.

## The Problem

A car's tracked position jumps, yet every sensor reading is correct: the two computers' clocks disagree. And a failed run is hard to trace unless each step logged its state.

## The Concept

A robot understands its sensors only if every reading is placed at the moment it was taken.

![Four timestamps](../assets/diagram-offset-exchange.png)

*One computer asks the other for its time and notes when it asked and when the answer came back.*

The request's note shows the clock gap plus the trip time, and the reply's shows the gap minus it. Averaging cancels the trip. Trust the try with the shortest round trip, whose error is smallest.

![Offset estimate and order errors](../assets/fig-time-sync.png)

*Left: the best of several tries beats a single one. Right: sensors close in time swap order once the clock offset is big enough.*

A trace logs the state before and after each step. A trace reader (a small checking program) checks each step against its intent and names the first one that went wrong.

![Trace reader](../assets/diagram-trace-reader.png)

*The reader checks intents in order and stops at the first mismatch.*

![Arm skips target two](../assets/clip-example.mp4)

*The arm misses the middle target. The reader turns the first green, the second red, then stops.*

<details><summary>The math (optional)</summary>

The client sends a request at `t0` and gets the reply at `t3`. The server receives at `t1` and replies at `t2`. The offset is `((t1 - t0) + (t2 - t3)) / 2`. If the server clock is 50 ms ahead and each trip takes 20 ms, `t1 - t0` is 70 ms and `t2 - t3` is 30 ms, so the average is 50 ms. With 30 ms out and 10 ms back the estimate is off by 10 ms, half the difference of the delays. The error is at most half the round trip, so the shortest one is the most trustworthy. A camera clock 30 ms ahead can give a camera sample taken first a later stamp than an IMU sample taken after it. The figure uses the best of 8 tries and sensors 10 ms apart. The reader reports `not_executed`, `no_motion` or `wrong_motion`.

</details>

## Build It

```python
def estimate(t0, t1, t2, t3):
    return ((t1 - t0) + (t2 - t3)) / 2, (t3 - t0) - (t2 - t1)
```

`order_errors()` counts readings that land in the wrong place when sorted by time stamp. `first_mismatch()` returns the first failing intent.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/04-time-sync-and-traces -q
```

## Use It

`estimate()` follows the standard clock-sync formulas (NTP).

Sources: RFC 5905 (https://datatracker.ietf.org/doc/html/rfc5905) and ROS 2 design article "Clock and Time" (https://design.ros2.org/articles/clock_and_time.html), both read 2026-11-09.

## Ship It

`outputs/skill-trace-first-mismatch.md` names a trace's first failing step.

## Exercises

1. Give the camera clock a bigger offset and count the order errors.
2. Make the outgoing and return delays differ and see the error.
3. Break one step of a trace and see what the reader says.
