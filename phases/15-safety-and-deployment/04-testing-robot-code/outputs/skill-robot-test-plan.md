---
name: robot-test-plan
description: Use when writing or reviewing tests for robot control code that depends on time, a joint or hardware inputs (a controller, watchdog, limit check or safety monitor). Produces a plan of unit tests with a fake clock and mock joint, a replay test from a recorded trace, and property-style tests.
---

# Robot test plan

1. Put the clock behind an object the code receives. In tests pass a fake with `now()` and `advance(dt)`. Never sleep.
2. Replace the joint with a mock that integrates a simple plant, records every command, and raises on a command over its limit or NaN.
3. Unit tests: one per behaviour with a time or limit rule (stale gap gives zero output, direction toward target, saturation). Include a step-direction test so a wrong sign fails loudly.
4. Replay test: record a good run as `(inputs, output)` rows, store it as a file, feed the inputs to the current code and assert the outputs. When it fails, a person decides whether the change was intended before re-recording.
5. Property test: seeded random inputs, including NaN, infinity and huge values and odd time steps. Assert finite output within limits.
6. Report which tests would have failed for each fault in the fault-injection list and which faults no test covers.

Do not weaken a test to make it pass. Return the plan as a list of test names with the bug each one catches.
