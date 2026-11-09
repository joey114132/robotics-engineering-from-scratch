---
name: executor-starvation-check
description: Use when a ROS 2 timer or subscription fires late or in bursts while the CPU is mostly idle, or when a heartbeat or watchdog node misses deadlines. Finds the callback holding the executor thread and picks the fix.
---

# Executor starvation check

1. List every callback of the node with its period (or message rate) and its measured duration. Add timestamps at callback entry and exit if the duration is unknown; do not guess it.
2. Name the executor type, the number of threads, and the callback group of each callback. Callbacks created without a group are in the node's default group.
3. For each late callback, find the longest other callback that shares its thread or its mutually exclusive group. Its duration bounds the wait. If the wait is longer than the late callback's period, ticks are being missed.
4. Choose the smallest fix. First split the slow work into short pieces or move it out of the callback. Then give the slow callback its own group and run a multi-threaded executor. Adding threads without separating groups changes nothing.
5. Re-measure the late callback's wait after the change and report before and after.

Return the blocking callback, its duration, the late callback's worst wait, and the chosen fix. Never raise a thread count or change a group on a shared robot without saying so.
