# ROS 2 in One Page

> Learn how robot programs pass data to each other, and why a longer waiting line can make a robot react late.

**Type:** Learn   **Prerequisites:** 00/07 Python Env and numpy   **Time:** ~15 minutes

## In Plain Words

A sensor tracks a cup sliding along a table and reports faster than the arm's controller (the program that steers the arm) can read. Unread reports wait in a queue, and the controller takes the oldest first.

A full queue drops its oldest report for each new one. A long queue means the oldest report can be half a second old. A queue of one always gives the newest.

## Key Terms

- **ROS 2**: robot software that splits a robot into small programs that pass messages to each other.
- **Node**: one running program in a ROS 2 system.
- **Topic**: a named stream. A program that sends into it is a publisher; a program that reads from it is a subscriber.
- **Service**: a request with one reply, unlike a topic's endless stream.
- **Queue depth**: how many messages a subscriber keeps while it waits to read them.
- **QoS**: quality of service, the settings that decide how messages are kept and delivered.

## The Problem

A robot's controller reads joint angles only 40 times a second, but the motor program sends them 100 times a second. To avoid losing messages you make the waiting line 50 long, and now the arm reacts late.

## The Concept

A robot is many small programs, and how they pass data decides how fresh it arrives.

![Topics and services](../assets/diagram-ros-parts.png)

*Programs send a stream (topic) or ask one question and get one answer (service).*

Each reader keeps a waiting line of messages. When the line is full, a new message pushes the oldest out. A longer line only means older data.

![Slow subscriber](../assets/diagram-queue-depth.png)

*The sender is faster, so the line stays full.*

[![Three arms, three queue depths](../assets/clip-example.jpg)](../assets/clip-example.mp4)

*Short, medium and long lines. The longer the line, the more the arm chases old positions.*

![Queue depth](../assets/fig-queue-depth.png)

*A longer line does not save messages. It only makes the ones you read older.*

<details><summary>The math (optional)</summary>

Run 10 s with a 100 Hz (times per second) sender and a 40 Hz reader: 1000 messages are sent and 400 are read at every depth. The message read is 5 ms old at depth 1, and each extra queued message adds 10 ms: 95 ms at depth 10, 495 ms at depth 50. Messages arrive every 10 ms, so 50 queued ones reach back 0.5 s.

</details>

## Build It

The `Bus` keeps one waiting line per reader. `run()` counts messages thrown away (drops) and how old each message is when read (age). `burst_drops()` shows the one case where a longer line helps: many messages arriving at once.

```python
def publish(self, topic, msg):
    for s in self.subs.get(topic, []):
        if len(s.q) == s.depth:
            s.q.popleft()
            s.dropped += 1
        s.q.append(msg)
```

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-start-here/10-ros2-in-one-page -q
python3 phases/00-start-here/10-ros2-in-one-page/code/main.py
```

## Use It

In ROS 2 this is the QoS setting `keep last` plus a depth. Keep it short for control signals.

Sources: https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html

## Ship It

`outputs/skill-qos-depth-check.md` checks a topic's rates and depth for drops and stale data.

## Exercises

1. Compare message age at depth 1 and depth 50.
2. Make the reader faster than the sender and run `run()`.
3. Add a second reader with another depth.
