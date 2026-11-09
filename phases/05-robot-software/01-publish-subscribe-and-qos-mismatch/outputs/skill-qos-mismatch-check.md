---
name: qos-mismatch-check
description: Use when a ROS 2 topic has both a publisher and a subscriber but the subscriber receives nothing, or receives far fewer messages than published. Walks QoS profiles, compatibility and queue depth.
---

# QoS mismatch check

1. List the QoS profile of every publisher and subscriber on the topic: reliability, durability, depth, and deadline if set. Read them from the node code or the introspection tools, never from memory of the defaults.
2. For each pair, apply request versus offered. Best effort publisher with a reliable subscriber fails. Volatile publisher with a transient-local subscriber fails. A subscriber deadline shorter than the publisher's fails. Report the first failing policy per pair.
3. If every pair is compatible, compare the average publish rate with the callback's average consume rate. A queue depth covers a burst only; a consumer slower on average drops messages at any depth.
4. Check whether the link is lossy. Best effort on a lossy link loses samples by design.
5. Fix the subscriber profile to match the publisher, not the other way round, unless the publisher is yours and the guarantee is really needed.

Return the failing pair, the failing policy, and the smallest profile change. Never change a profile on a shared robot without saying so.
