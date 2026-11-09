---
name: imitation-data-check
description: Use before training a policy on demonstrations, or when a cloned policy fails on starts the expert handles. Checks coverage, multimodality and sample count of the demo set.
---

# Imitation data check

1. Count demonstrations and distinct start states. Plot success rate against the number of demos on held-out starts; if the curve is still rising, collect more.
2. Look for modes: places where the expert goes left on one run and right on another. A smooth regressor averages them. Use a local or multimodal model, or make the expert consistent.
3. Hold out starts the policy never saw. Report success on those, never on the training starts.
4. Define success by the task (no contact, reached goal), not by closeness to the expert path.

Return the demo count, held-out success rate, and any state region with no demos. Never tune on the test starts.
