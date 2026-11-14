# Control Loop Jitter

> The average period of a loop can be perfect while one late wake-up in a few thousand breaks the controller.

**Type:** Build   **Prerequisites:** 05/02 Executors and Callbacks   **Time:** ~15 minutes

## In Plain Words

A control loop gives an arm a new target on every beat, like a metronome. If each beat waits one period after the previous move finishes, every beat comes a little later and the arm falls behind. If each beat is fixed on the clock, the beats stay on schedule. Rarely, another program holds the processor and one wake-up comes late, so the arm twitches. The average hides that one late beat, so check the worst delay and the missed deadlines too.

## The Problem

A 1 kHz control loop, which wakes 1000 times a second to command an arm, reports a mean period of exactly 1.000 ms. Yet the arm twitches once every few seconds. The mean covers thousands of good cycles, so a single bad one barely moves it, but the twitch comes from that bad one.

## The Concept

![One turn of a fixed-rate loop](../assets/diagram-loop-anatomy.png)

*Follow the numbers: each turn sleeps until a fixed time, wakes a little late, works, and must finish before the next deadline, when the next turn is due.*

Jitter is the period minus the target period T. Sleeping until `i * T` (turn i's own fixed time) keeps the mean at T, so late wake-ups show up only as spread. Sleeping T after the work adds the work time to every cycle, and the loop drifts slow.

![Mean versus worst](../assets/diagram-average-hides.png)

*Mean, standard deviation and even p99 (the delay 99% of cycles stay under) can look healthy. The motor is driven by the single worst cycle.*

Example: in this run, cycle 2098 wakes 1.5 ms late. Its 0.2 ms of work ends 0.7 ms after the next slot (1.5 + 0.2 - 1.0), so the next cycle starts 0.7 ms late too. So the arm's command goes out late and the arm waits while the target moves on.

![An arm falling behind its target at one late wake-up](../assets/clip-example.mp4)

*Watch the arm and the amber ball. The ball steps on schedule and the arm steps when its command really goes out, so it stays behind once and then jumps. The motion is drawn ten cycles long and played 450 times slower.*

![Jitter histogram and timeline](../assets/fig-jitter.png)

*In this run of 5000 cycles (random numbers fixed by a seed) the mean jitter is 0 us (microseconds) and p99 is 113 us, but the worst is 1498 us, 1.5 ms, and 5 deadlines are missed.*

## Build It

```python
wake = (done + T if relative else i * T) + lat[i]
s[i] = max(wake, done)
d[i] = done = s[i] + work
```

`simulate()` draws small random wake-up delays (exponential) plus rare spikes of 0.5 to 1.5 periods. `stats()` reports mean, p99 and worst jitter, and counts iterations that finish after their next deadline. The spikes are a model of preemption, not a measurement.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/03-control-loop-jitter -q
python3 phases/05-robot-software/03-control-loop-jitter/code/main.py
```

## Use It

On Linux, `clock_nanosleep` with `TIMER_ABSTIME` sleeps to an absolute time, which is the `i * T` mode here. Compare your simulated worst case with a measured one from your own loop before trusting it.

Sources: clock_nanosleep(2) (https://man7.org/linux/man-pages/man2/clock_nanosleep.2.html) and ROS 2 Jazzy "Understanding real-time programming" (https://docs.ros.org/en/jazzy/Tutorials/Demos/Real-Time-Programming.html), both read 2026-11-09.

## Ship It

`outputs/skill-loop-jitter-report.md` turns a list of loop timestamps into a mean, p99, worst and miss report.

## Exercises

1. Raise `spike_p` until the p99 also looks bad, and note how many cycles that takes.
2. Find the period right after each miss and explain why it is shorter than normal.
3. Add a watchdog that trips after two consecutive misses and report how often it trips.
