# ROS 2 in One Page

> Nodes exchange data over topics and services, and a queue depth decides what a slow subscriber loses.

**Type:** Learn   **Prerequisites:** 00/01 Python Env and numpy   **Time:** ~15 minutes

## In Plain Words

Class chat messages arrive faster than you can read them. If you always read the oldest unread message, a
larger inbox lets you spend longer catching up with news that is already out of date.

A subscriber queue works like that inbox. With keep last, new messages evict the oldest when it fills.
Increasing depth preserves more waiting messages, but it does not make a slow reader faster. Under a steady
overload, the reader gets older data.

## The Problem

Your controller reads joint states at 40 Hz while the driver publishes at 100 Hz. You raise the queue depth to 50 to stop losing messages, and the arm now reacts half a second late. The setting that looked like a safety margin turned old data into the thing you read.

## The Concept

![Nodes talk over topics and services](../assets/diagram-ros-parts.png)

*A node is a program. A topic carries a stream from publishers to subscribers. A service answers one request with one reply.*

A subscriber owns a queue. With the history policy "keep last", the queue holds at most `depth` messages, and a new message pushes out the oldest one when it is full.

![A slow subscriber and a short queue](../assets/diagram-queue-depth.png)

*The publisher is faster than the subscriber, so the queue is always full and the oldest message is dropped on every publish.*

![Queue depth against message age](../assets/fig-queue-depth.png)

*Left: the subscriber reads messages about `(depth - 1)` publish periods old. Right: the same 400 messages are delivered at every depth. Depth only moves messages between "dropped" and "still queued".*

## Build It

A `Bus` with named topics and one queue per subscription. No ROS install is needed.

```python
def publish(self, topic, msg):
    for s in self.subs.get(topic, []):
        if len(s.q) == s.depth:
            s.q.popleft()
            s.dropped += 1
        s.q.append(msg)
```

`run(pub_hz, sub_hz, depth, seconds)` stamps each message with its send time and takes one per subscriber tick, so it can report drops and the age of what was read. `burst_drops()` shows the case where depth does help: a burst shorter than the queue.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-setup-and-tooling/04-ros2-in-one-page -q
python3 phases/00-setup-and-tooling/04-ros2-in-one-page/code/main.py
```

## Use It

In ROS 2 the same setting is the QoS history policy `keep last` with a queue depth; the QoS page supports only that. The advice that follows is this lesson's own: keep a small depth for control signals where only the newest value matters, and size a larger one for bursts. Match the subscriber rate to the publisher before raising depth.

Sources: https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html

## Ship It

`outputs/skill-qos-depth-check.md` reviews a topic's rates and depth and says whether data will be dropped or stale.

## Exercises

1. Add a "keep all" subscription and show how its queue grows.
2. Plot the age of messages when the subscriber is faster than the publisher.
3. Add a second subscriber with a different depth on the same topic.
