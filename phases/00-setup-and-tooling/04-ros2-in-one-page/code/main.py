# 레슨 00/04: topic, queue depth, drop 이 있는 장난감 publish/subscribe bus 와 느린 subscriber 시뮬레이션
from collections import deque

import numpy as np


class Subscription:
    def __init__(self, depth):
        self.q, self.depth, self.dropped = deque(), depth, 0


class Bus:
    """In-process topics. Each subscription keeps the last `depth` messages (history KEEP_LAST)."""

    def __init__(self):
        self.subs = {}

    def subscribe(self, topic, depth):
        s = Subscription(depth)
        self.subs.setdefault(topic, []).append(s)
        return s

    def publish(self, topic, msg):
        for s in self.subs.get(topic, []):
            if len(s.q) == s.depth:  # full: the oldest message is thrown away
                s.q.popleft()
                s.dropped += 1
            s.q.append(msg)

    def take(self, s):
        return s.q.popleft() if s.q else None


def run(pub_hz, sub_hz, depth, seconds):
    """Publisher stamps each message with its send time; the subscriber takes one message per tick."""
    bus = Bus()
    s = bus.subscribe("/joint_states", depth)
    events = [(i / pub_hz, 0) for i in range(int(seconds * pub_hz))] + [(j / sub_hz, 1) for j in range(int(seconds * sub_hz))]
    ages, published = [], 0
    for t, kind in sorted(events):  # at equal times the publish (0) comes before the take (1)
        if kind == 0:
            bus.publish("/joint_states", t)
            published += 1
        elif (stamp := bus.take(s)) is not None:
            ages.append(t - stamp)
    return dict(published=published, delivered=len(ages), dropped=s.dropped, ages=np.array(ages))


def burst_drops(burst, depth):
    bus = Bus()
    s = bus.subscribe("/q", depth)
    for i in range(burst):
        bus.publish("/q", i)
    return s.dropped


if __name__ == "__main__":
    for d in (1, 10, 50):
        r = run(100, 40, d, 10.0)
        print(f"depth {d:3d}: delivered {r['delivered']}, dropped {r['dropped']}, last age {r['ages'][-1] * 1000:.0f} ms")
