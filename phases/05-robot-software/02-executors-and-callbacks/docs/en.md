# Executors and Callbacks

> One thread runs one callback at a time, so a slow callback makes every other callback wait, whatever its period.

**Type:** Build   **Prerequisites:** 05/01 Publish-Subscribe and QoS Mismatch   **Time:** ~15 minutes

## In Plain Words

A toy car drives only while a heartbeat timer keeps ticking. If a tick comes late, a watchdog, a guard that checks the heartbeat, stops the car. The car's program has one worker, called a thread, and a worker does one job at a time. While it grinds through a long image job, the heartbeat waits in line and the car stops.

A second worker could run the heartbeat meanwhile, unless a rule bans overlap, as when both jobs edit the same data. Callback groups hold that rule.

## The Problem

A node has a timer that fires 100 times a second to send a heartbeat, and a subscription whose callback, the function ROS 2 runs for each message, does 60 ms of image work. The heartbeat stutters, and a watchdog elsewhere declares the node dead. Every callback is correct on its own, and the CPU is mostly idle.

## The Concept

![One thread, one slow callback](../assets/diagram-executor-starve.png)

*Both callbacks need the one thread, so the timer waits for the whole slow callback.*

An executor decides which ready callback runs next and on which thread. Callbacks are grouped. A mutually exclusive group never runs two of its callbacks at once, which protects data they share. Callbacks of different groups may run in parallel.

![Threads and groups](../assets/diagram-callback-groups.png)

*Read each row left to right. A second thread helps only if the two callbacks sit in different groups.*

Example: the slow callback starts at 0 ms and holds its thread for 60 ms. The timer is ready at 1 ms, so with one thread, or two threads and one group, it waits 59 ms, the worst wait `simulate()` reports. In separate groups a second thread starts it at once, so it waits 0.

![Two cars, two threads each](../assets/clip-example.mp4)

*Each roof lamp is a thread, lit while it works. Blue shares one group: its second lamp stays dark and the car keeps stopping. Green has separate groups: both lamps work and it never stops.*

![Timeline of both setups](../assets/fig-executor-timeline.png)

*One thread: the timer starts up to 59 ms late. Two threads, separate groups: never.*

## Build It

```python
busy = {g for _, g in running if g is not None}
job = next((j for j in pending if j[3] is None or j[3] not in busy), None)
```

`simulate()` advances time in 1 ms steps. Each step releases the periodic callbacks, frees finished jobs, and gives every free thread the oldest pending job whose group is idle. `latencies()` returns the wait between release and start. The model is first come, first served (FIFO) and queues every missed tick. The documentation says an overloaded executor takes ready work in turns (round-robin), so read its "Scheduling semantics" section before comparing numbers.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/02-executors-and-callbacks -q
python3 phases/05-robot-software/02-executors-and-callbacks/code/main.py
```

## Use It

ROS 2 offers single-threaded and multi-threaded executors and mutually exclusive or reentrant (may overlap with its group-mates) callback groups. Callbacks created without a group join the node's default group, so give the slow callback its own group before adding threads, if they share no data.

Sources: ROS 2 Jazzy, "Executors" (https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Executors.html), read 2026-11-09 from its source file in the `jazzy` branch of ros2/ros2_documentation.

## Ship It

`outputs/skill-executor-starvation-check.md` finds the callback that starves the others and says which fix applies.

## Exercises

1. Add a reentrant group (`None`) with two slow jobs and show they overlap on two threads.
2. Make the timer drop missed ticks instead of queueing them and compare the worst wait.
3. Split the slow callback into six 10 ms chunks and report the timer's worst wait on one thread.
