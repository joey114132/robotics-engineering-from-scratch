---
name: loop-jitter-report
description: Use when a periodic control or sensor loop is said to run at some rate and you need to know whether it is good enough, or when a robot twitches at irregular intervals. Turns loop timestamps into mean, p99, worst case and deadline misses.
---

# Loop jitter report

1. Record the start time and the finish time of every iteration for at least a few minutes, on the real hardware and under normal load. Use a monotonic clock.
2. Compute the period of each iteration as the difference of start times, and the jitter as period minus the target. Never report the mean alone.
3. Report mean, standard deviation, p99 of the absolute jitter, the worst case, and the number of iterations that finished after their next deadline. Give the sample count so a reader can see how rare the worst case is.
4. Look at the timeline, not only the histogram. Check whether the spikes are periodic, which points to another task or a timer, or random, which points to preemption or a shared resource.
5. Check whether the loop sleeps to an absolute time or for a relative duration. A relative sleep drifts slow by the work time.

Return the five numbers, the miss count, and one sentence naming the likely source of the worst case. Never state that a loop is real-time from a mean.
