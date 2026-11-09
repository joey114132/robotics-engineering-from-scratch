---
name: trace-first-mismatch
description: Use when a robot run, test or demo failed and a JSONL execution trace with pre and post state per step exists, or when sensor streams from different machines disagree in time. Finds the first step that did not match its intent and checks clock offsets.
---

# Trace first mismatch

1. Collect the intent list (step, primitive, target) and the trace lines. Each trace line needs the step number, the state before (`pre`) and the state after (`post`). If a trace has no pre and post pair, say so; the run cannot be judged from it.
2. Walk the intents in order. For each one report the first of three outcomes. No record: not executed. Record with unchanged state although a move was intended: no motion. State moved but away from the target by more than the tolerance: wrong motion.
3. Stop at the first mismatch. Later failures are usually consequences. Report the step, the kind, the pre, the post and the target.
4. If the trace joins streams from more than one machine, check their clocks first. Compare timestamps of a shared event, or run an offset estimate from request and reply times and use the exchange with the smallest round trip. An offset larger than the gap between events reorders them.
5. State the tolerance you used and why. Never widen it to make the run pass.

Return the first mismatching step with its kind and the numbers behind it, plus the clock offset if relevant. Never run a robot command to reproduce the failure without approval.
