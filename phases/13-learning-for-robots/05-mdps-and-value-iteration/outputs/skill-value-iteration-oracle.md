---
name: value-iteration-oracle
description: Use when a learned policy needs a reference answer on a small simulated task, or when someone asks whether a reward and discount produce the behaviour they want. Computes exact values and the greedy policy for a discretised model.
---

# Value-iteration oracle

1. Discretise the task into states, actions, transition probabilities and rewards. Write down which states end the episode. Stop if the model has more than a few thousand states.
2. Use finite rewards, normalized transition probabilities, `0 < gamma < 1` and `tol > 0`. Measure `delta1 = max(abs(V1 - V0))`. Contraction gives `delta_k <= gamma**(k - 1) * delta1`. Stop only when `delta_k < tol`; the bound below includes the first change and checks the strict inequality. Also check that a backup leaves at most `gamma` times the gap between two value tables.
3. Extract the greedy policy and evaluate it exactly. Its value must equal the iterated values.
4. Print the value map and the arrows, and look at them. A policy that hugs a penalty cell or a wall usually means a reward or slip probability is wrong.
5. Compare any learned policy's return from the same start cell with `V`.

For the first sweep counted as `k = 1`, the bound is one sweep when `delta1 < tol`; otherwise it is `2 + floor(log(tol / delta1) / log(gamma))`. Verify the strict inequality directly to avoid rounding at exact powers.

```python
import math


def sweep_bound(delta1, gamma, tol):
    assert delta1 >= 0 and 0 < gamma < 1 and tol > 0
    bound = 1 if delta1 < tol else 2 + math.floor(math.log(tol / delta1) / math.log(gamma))
    while delta1 * gamma**(bound - 1) >= tol:
        bound += 1
    return bound
```

Return `V`, the policy, the sweep count and the gap between a learned policy and `V`. Never use the oracle for a robot whose model you have not validated.
