# 레슨 05/01: 발행자와 구독자의 QoS 호환 검사, 그리고 가득 차면 가장 오래된 것을 버리는 keep-last 큐
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Qos:
    reliability: str = "reliable"  # "reliable" or "best_effort"
    durability: str = "volatile"  # "volatile" or "transient_local"
    depth: int = 10


def compatible(pub: Qos, sub: Qos) -> tuple[bool, str]:
    """Request vs offered: the subscriber may not ask for more than the publisher offers."""
    if pub.reliability == "best_effort" and sub.reliability == "reliable":
        return False, "reliability: publisher offers best_effort, subscriber requests reliable"
    if pub.durability == "volatile" and sub.durability == "transient_local":
        return False, "durability: publisher offers volatile, subscriber requests transient_local"
    return True, "ok"


class Queue:
    """Keep-last history: at most `depth` messages, the oldest is dropped first."""

    def __init__(self, depth: int):
        self.depth, self.items, self.dropped = depth, [], 0

    def push(self, msg):
        self.items.append(msg)
        if len(self.items) > self.depth:
            self.items.pop(0)
            self.dropped += 1


def run(pub: Qos, sub: Qos, arrivals, link_loss: float = 0.0, seed: int = 0) -> dict:
    """arrivals[t] messages are published at tick t; the subscriber callback takes one per tick."""
    ok, why = compatible(pub, sub)
    published = int(sum(arrivals))
    out = dict(connected=ok, reason=why, published=published, delivered=0, dropped=0, lost=0)
    if not ok:  # the silent failure: both ends exist, nothing is delivered
        return out
    rng, q, t = np.random.default_rng(seed), Queue(sub.depth), 0
    lossy = not (pub.reliability == "reliable" and sub.reliability == "reliable")
    while t < len(arrivals) or q.items:
        for _ in range(arrivals[t] if t < len(arrivals) else 0):
            if lossy and rng.random() < link_loss:
                out["lost"] += 1  # best_effort: no retry
            else:
                q.push(t)
        if q.items:
            q.items.pop(0)
            out["delivered"] += 1
        t += 1
    out["dropped"] = q.dropped
    return out


if __name__ == "__main__":
    print(run(Qos("best_effort"), Qos("reliable"), [1] * 20))
    print(run(Qos(), Qos(depth=1), [8] + [0] * 9))
