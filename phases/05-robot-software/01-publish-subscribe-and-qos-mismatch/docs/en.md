# Publish-Subscribe and QoS Mismatch

> A subscriber may not ask for more than the publisher offers, and when it does, nothing is delivered and nothing complains.

**Type:** Build   **Prerequisites:** 00/04 ROS 2 in One Page   **Time:** ~15 minutes

## In Plain Words

A rover tells a robot arm where it is by sending short messages, and the arm follows using only what it receives. Before they connect, each side states a delivery promise, called QoS (quality of service). The rover promises only to try, and the arm insists on guaranteed delivery.

The arm asks for more than the rover offers, so they never connect. The rover sends and nobody complains, but nothing arrives and the arm stays still. A rover that promised guaranteed delivery would connect to an arm asking for less.

## The Problem

A rover node, a running program, publishes its position on a topic, a named channel. An arm node subscribes to that topic, meaning it listens there, yet the arm never moves. Both nodes run and nothing crashes. The two sides asked for different delivery guarantees, so the software that carries the messages never connected them.

## The Concept

![Request versus offered](../assets/diagram-qos-match.png)

*Follow the arrows: the rover offers best effort and the arm asks for reliable. The arm asks for more than is offered, so there is no match.*

Each side declares a QoS profile. Reliability: best effort sends once and moves on, reliable resends a lost message. Durability: volatile gives a late subscriber nothing, transient local gives it the old messages. History depth: how many unread messages may wait. A pair connects only if the subscriber asks for no more than the publisher offers, so reliable and transient local are the bigger asks. A reliable publisher with a best effort subscriber is fine. The reverse is not.

![Queue with depth](../assets/diagram-qos-queue.png)

*A keep-last queue holds the newest N and drops the oldest when a new one arrives.*

Even a matched pair loses messages when the callback, the function that handles each message, is slower than the publisher.

Example: the rover sends 8 position messages in one burst and the arm handles one per tick, a tick being one simulation step. With depth 1, `run()` delivers 1 and drops 7, so the arm sees only the last position. With depth 8 it delivers all 8.

![Eight messages reaching two arms](../assets/clip-example.mp4)

*Same burst, two shelves. The blue shelf has one slot: seven messages fall and the arm moves once. The green shelf has eight slots: the arm steps through all.*

![Delivery and drops](../assets/fig-qos-delivery.png)

*Left: only the mismatched pair delivers 0%. Right: a burst of 8 needs depth 8. A constant overload, 2 messages per tick for a callback taking 1, drops half at any depth.*

## Build It

```python
def compatible(pub, sub):
    if pub.reliability == "best_effort" and sub.reliability == "reliable":
        return False, "reliability: ..."
    if pub.durability == "volatile" and sub.durability == "transient_local":
        return False, "durability: ..."
    return True, "ok"
```

`Queue.push()` appends and pops the oldest past `depth`, counting drops. `run()` publishes `arrivals[t]` messages per tick, loses some on a best effort link, and lets the callback take one per tick.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/01-publish-subscribe-and-qos-mismatch -q
```

## Use It

Compare `compatible()` with the tables in the ROS 2 QoS documentation, and with the incompatible-QoS events that publishers and subscriptions can report.

Sources: ROS 2 Jazzy, "Quality of Service settings" (https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html), read 2026-11-09 from its source file in the `jazzy` branch of ros2/ros2_documentation.

## Ship It

`outputs/skill-qos-mismatch-check.md` walks a silent topic through profile, compatibility and queue checks.

## Exercises

1. Add a deadline policy and a rule that rejects a subscriber deadline shorter than the publisher's.
2. Give `Queue` a keep-all mode and show the memory it needs under sustained overload.
3. Make a transient-local publisher replay its last `depth` messages to a late subscriber.
