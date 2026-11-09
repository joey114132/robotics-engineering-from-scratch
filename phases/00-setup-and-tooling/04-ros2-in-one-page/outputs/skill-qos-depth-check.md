---
name: qos-depth-check
description: Use when a ROS 2 subscriber loses messages or reacts late, or before choosing a QoS history depth for a topic. Compares publisher and subscriber rates and predicts drops and message age.
---

# QoS depth check

1. Write down, per topic, the publish rate, the subscriber's real processing rate, and the configured history policy and depth.
2. If the subscriber is slower than the publisher for longer than a short burst, drops are certain whatever the depth. Say so, and fix the rate (process less per message, run faster, or lower the publish rate) first.
3. For keep-last, estimate the age of the data read as about `(depth - 1) / publish_rate` plus up to one subscriber period. Flag any control topic where that age exceeds the control period.
4. Size depth for the longest expected burst only, and use depth 1 where only the newest value matters.

Report the topic, the rates, predicted drops per second and predicted message age. Do not change QoS settings on a running system.
