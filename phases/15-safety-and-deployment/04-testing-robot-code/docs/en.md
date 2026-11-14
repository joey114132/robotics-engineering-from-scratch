# Testing Robot Code

> A robot test must control time, refuse bad commands, and replay what really happened.

**Type:** Build   **Prerequisites:** 15/01 Failure Modes   **Time:** ~15 minutes

## In Plain Words

Testing a timer app does not mean waiting for the alarm: you jump its pretend clock past the deadline. A robot test does the same: it moves a fake clock by hand, so a second of arm motion takes no time, then asks one question: when the target jumps ahead (a step), does the joint move closer?

A controller with its sign flipped pushes the arm away, so that test fails at once. A mock joint, a pretend arm, refuses bad torque. Replaying a recorded run shows which command changed.

## The Problem

Robot code depends on a clock, a joint and inputs you cannot predict, so tests either sleep for seconds, need hardware, or check nothing. The wrong-sign fault from lesson 01 shows it. The joint ran away, and a test that only checks "it returns a number" passes.

## The Concept

![Three tests, three kinds of bug](../assets/diagram-test-kinds.png)

*Unit: step the fake clock, check one rule ("closer after 0.3 s?"). Replay: feed recorded readings back, compare torque. Property: throw thousands of random inputs at one rule.*

![The test owns the clock](../assets/diagram-fake-clock.png)

*The controller asks an object for the time. In production that is the real clock; in a test, a fake the test advances, so ten seconds pass instantly and the result never varies.*

![A sign bug seen by two tests](../assets/fig-sign-bug.png)

*Left: the step test fails because the joint ends far from the target after 0.3 s. Right: replaying recorded inputs through the buggy controller gives the mirror image of the recorded torque.*

Replay example. A step of 1.0 rad gives `kp * error = 40 * 1.0 = 40`, clipped to `tau_max` 10, so the recorded first torque is +10.0. The flipped controller, fed the same recorded readings, answers -10.0 first and then the mirror of every recorded torque, all 80 samples, 10 ms apart. The replay test fails at the first.

![Two bench arms replay one recording, and the flipped controller pushes the opposite way](../assets/clip-example.mp4)

*Both arms replay one recording. The red arrow is each controller's torque: green pushes toward the target, blue (sign flipped) the opposite way.*

![Torque over random inputs](../assets/fig-property-torque.png)

*The property test draws thousands of random inputs and checks one rule: torque is finite and never over the limit.*

## Build It

`FakeClock` has `now()` and `advance(dt)`. `MockJoint` integrates a simple plant and raises if it is handed a torque over its limit, NaN (not a number) included. `Controller` is a PD loop that gives zero torque when the gap between updates exceeds a timeout. `run()` returns the trace as `(q_meas, q_ref, tau)` rows.

```python
def test_step_direction_test_catches_the_sign_bug():
    with pytest.raises(AssertionError, match="moved away"):
        check_step_direction(polarity=-1)
```

`code/tests/golden_trace.json`, the trusted recording, came from the healthy controller. Without its non-finite guard the property test fails on NaN input, so the controller returns zero torque for NaN and infinity.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/04-testing-robot-code -q
python3 phases/15-safety-and-deployment/04-testing-robot-code/code/main.py
```

## Use It

In a ROS 2 node, inject the clock the same way, or use simulated time. Record real bags of a good run and replay them through new code before each release. A property-testing library such as hypothesis can run that kind of search.

## Ship It

`outputs/skill-robot-test-plan.md` turns a controller into a list of unit, replay and property tests.

## Exercises

1. Change `kp` and watch the replay test fail, then decide whether to re-record.
2. Write a property test that a stale controller always returns exactly zero.
3. Add a test for a swapped `q_meas` and `q_ref` argument order.
