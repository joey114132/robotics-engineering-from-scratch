# Control Loop Jitter

> Learn why a control loop with a perfect average timing can still make a robot arm twitch.

**Type:** Build   **Prerequisites:** 05/02 Executors and Callbacks   **Time:** ~15 minutes

## In Plain Words

A control loop gives an arm a new target on every beat, like a metronome. If each beat waits one period after the last move, the beats drift later and later. Beats fixed on the clock stay on schedule. Rarely, another program holds the processor, one wake-up comes late and the arm twitches.

## Key Terms

- **Control loop**: code that repeats at a fixed rate to read sensors, compute and command the motors.
- **Period (`T`)**: the planned time between two turns of the loop.
- **Jitter**: how far a turn's real timing is from the plan.
- **Deadline**: the time by which a turn must finish.
- **p99**: the delay that 99% of cycles stay under.
- **Preemption**: the operating system pausing your program to run another one.

## The Problem

A robot arm twitches every few seconds, yet its control loop reports a perfect average timing. One bad cycle barely moves the average, but it causes the twitch.

## The Concept

An arm is only as steady as its slowest control cycle, not its average one.

![One turn of the loop](../assets/diagram-loop-anatomy.png)

*Each turn sleeps until a fixed time, wakes a little late, works, and must finish before the next deadline.*

Sleeping until a fixed time on the clock keeps the average perfect, so late wake-ups show up only as spread. One very late wake-up makes the next turn late too, so the arm's command goes out late while the target moves on.

![Mean versus worst](../assets/diagram-average-hides.png)

*Averages can look healthy. The motor is driven by the single worst cycle.*

![Arm behind its target](../assets/clip-example.mp4)

*The ball steps on schedule, the arm when its command goes out, so it lags once and then jumps.*

![Jitter histogram and timeline](../assets/fig-jitter.png)

*The average is perfect, yet the worst cycle is far off and a few deadlines are missed.*

<details><summary>The math (optional)</summary>

A 1 kHz loop wakes 1000 times a second and reports a mean period of exactly 1.000 ms. Sleeping until `i * T` keeps the mean at `T`. In this run cycle 2098 wakes 1.5 ms late, and its 0.2 ms of work ends 0.7 ms after the next slot (1.5 + 0.2 - 1.0), so the next cycle starts 0.7 ms late too. Over 5000 cycles (fixed seed) the mean jitter is 0 us (microseconds), p99 is 113 us, the worst is 1498 us and 5 deadlines are missed. Spikes are 0.5 to 1.5 periods long. The clip shows ten cycles played 450 times slower.

</details>

## Build It

```python
wake = (done + T if relative else i * T) + lat[i]
s[i] = max(wake, done)
d[i] = done = s[i] + work
```

`simulate()` draws small random wake-up delays plus rare spikes. `stats()` reports mean, p99 and worst jitter, and counts missed deadlines. The spikes model preemption and are not a measurement.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/03-control-loop-jitter -q
python3 phases/05-robot-software/03-control-loop-jitter/code/main.py
```

## Use It

On Linux, `clock_nanosleep` with `TIMER_ABSTIME` sleeps to an absolute time.

Sources: clock_nanosleep(2) (https://man7.org/linux/man-pages/man2/clock_nanosleep.2.html) and ROS 2 Jazzy "Understanding real-time programming" (https://docs.ros.org/en/jazzy/Tutorials/Demos/Real-Time-Programming.html), both read 2026-11-09.

## Ship It

`outputs/skill-loop-jitter-report.md` turns loop timestamps into a mean, p99, worst and miss report.

## Exercises

1. Make the rare spikes more common.
2. Explain why the period right after a miss is shorter.
3. Add a watchdog that trips after two misses in a row.
