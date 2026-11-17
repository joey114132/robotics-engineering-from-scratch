# Executors and Callbacks

> Learn why one slow task can freeze a robot's other tasks even when the processor is idle.

**Type:** Build   **Prerequisites:** 05/01 Publish-Subscribe and QoS Mismatch   **Time:** ~15 minutes

## In Plain Words

A toy car drives only while a heartbeat timer keeps ticking. If a tick is late, a watchdog stops the car. The car's program has one worker doing one job at a time, so a long image job makes the heartbeat wait.

## Key Terms

- **Callback**: a function ROS 2 runs when a message arrives or a timer fires.
- **Thread**: one worker inside a program, doing one job at a time.
- **Executor**: the part of ROS 2 that decides which ready callback runs next, and on which thread.
- **Callback group**: a set of callbacks that share one overlap rule, such as never running together.
- **Starvation**: a callback waits too long because another one holds the thread.
- **Watchdog**: a guard that stops the robot when a heartbeat is late.

## The Problem

A toy car stops suddenly. Its heartbeat timer stutters while another job does a long stretch of image work, and a watchdog stops the car though the processor is mostly idle.

## The Concept

A robot runs many jobs at once, and one slow job can starve the safety-critical ones.

![One thread, one slow callback](../assets/diagram-executor-starve.png)

*The timer waits for the whole slow callback.*

An executor decides which ready job runs next and on which worker. A mutually exclusive group never runs two of its jobs at once, which protects data they share. Jobs in different groups may run in parallel, if a second worker is free.

![Threads and groups](../assets/diagram-callback-groups.png)

*A second worker helps only if the two jobs sit in different groups.*

The fix needs a second worker and the slow job in its own group.

![Two cars, two threads each](../assets/clip-example.mp4)

*Each roof lamp is a worker. Blue shares one group, so its second lamp stays dark and the car stops. Green never stops.*

![Timeline of both setups](../assets/fig-executor-timeline.png)

*With one worker the timer starts very late. With two workers and separate groups it never does.*

<details><summary>The math (optional)</summary>

The timer sends a heartbeat 100 times a second and the subscription callback does 60 ms of image work. The slow callback starts at 0 ms and holds its thread for 60 ms. The timer is ready at 1 ms, so with one thread, or two threads and one group, it waits 59 ms. In separate groups it starts at once. The model is first come, first served, but ROS 2 takes ready work in turns, so read its "Scheduling semantics" before comparing numbers.

</details>

## Build It

```python
busy = {g for _, g in running if g is not None}
job = next((j for j in pending if j[3] is None or j[3] not in busy), None)
```

`simulate()` advances time in 1 ms steps and gives each free thread the oldest waiting job whose group is idle.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/02-executors-and-callbacks -q
python3 phases/05-robot-software/02-executors-and-callbacks/code/main.py
```

## Use It

Callbacks without a group share one default group, so give the slow callback its own before adding threads.

Sources: ROS 2 Jazzy, "Executors" (https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Executors.html), read 2026-11-09.

## Ship It

`outputs/skill-executor-starvation-check.md` finds the callback that starves the others and names the fix.

## Exercises

1. Put both callbacks in one group, then in two groups, and watch the timer.
2. Drop missed timer ticks instead of queueing them.
3. Split the slow callback into six 10 ms chunks and watch the timer.
