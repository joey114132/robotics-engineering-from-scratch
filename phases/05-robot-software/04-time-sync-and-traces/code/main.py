# 레슨 05/04: NTP 식 시계 offset 추정, 보정 안 된 시계가 센서 순서를 깨는 과정, JSONL trace 에서 첫 불일치 찾기
import json

import numpy as np


def exchange(offset, d_fwd, d_back, t0=0.0, proc=0.0):
    """One request/reply. offset = server clock minus client clock. Returns (t0, t1, t2, t3)."""
    t1 = t0 + d_fwd + offset  # server receives, on the server clock
    t2 = t1 + proc  # server replies
    t3 = t0 + d_fwd + proc + d_back  # client receives, on the client clock
    return t0, t1, t2, t3


def estimate(t0, t1, t2, t3):
    """Server minus client offset and round-trip delay. Exact when the two delays are equal."""
    return ((t1 - t0) + (t2 - t3)) / 2, (t3 - t0) - (t2 - t1)


def best_offset(samples):
    """Trust the exchange with the smallest round trip: it leaves the least room for asymmetry."""
    return min((estimate(*s) for s in samples), key=lambda od: od[1])[0]


def order_errors(a, b, b_offset, correction=0.0):
    """Sensor B's clock runs b_offset ahead. Count slots where the order sorted by stamp differs from the true order."""
    ev = [(t, "A") for t in a] + [(t, "B") for t in b]
    true = [k for _, k in sorted(ev)]
    stamped = [k for _, k in sorted((t + (b_offset - correction if k == "B" else 0.0), k) for t, k in ev)]
    return sum(x != y for x, y in zip(true, stamped))


def trace_line(step, primitive, pre, post):
    return json.dumps(dict(step=step, primitive=primitive, pre=list(pre), post=list(post)), sort_keys=True)


def first_mismatch(intents, lines, tol=1e-3, eps=1e-6):
    """Walk the intents in order and name the first one the trace does not show happening."""
    recs = {r["step"]: r for r in map(json.loads, lines)}
    for it in intents:
        r = recs.get(it["step"])
        if r is None:
            return {"step": it["step"], "kind": "not_executed"}
        moved = np.linalg.norm(np.subtract(r["post"], r["pre"])) > eps
        if not moved and np.linalg.norm(np.subtract(it["target"], r["pre"])) > tol:
            return {"step": it["step"], "kind": "no_motion"}
        if np.linalg.norm(np.subtract(r["post"], it["target"])) > tol:
            return {"step": it["step"], "kind": "wrong_motion"}
    return None


if __name__ == "__main__":
    print(estimate(*exchange(0.123, 0.03, 0.01)))
    print(order_errors([0.02 * i for i in range(50)], [0.02 * i + 0.01 for i in range(50)], 0.03))
