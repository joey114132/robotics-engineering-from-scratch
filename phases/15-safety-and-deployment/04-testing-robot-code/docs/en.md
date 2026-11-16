# Testing Robot Code

> Learn how to test robot code without waiting for real time and without risking a real robot.

**Type:** Build   **Prerequisites:** 15/01 Failure Modes   **Time:** ~15 minutes

## In Plain Words

Testing a timer app does not mean waiting for the alarm: you jump its pretend clock ahead. A robot test does the same, then asks: after the target jumps, does the joint move closer? A controller with its sign flipped pushes away, so that test fails at once.

## Key Terms

- **Fake clock**: a clock the test advances by hand.
- **Mock joint**: a pretend arm that refuses bad torque.
- **Unit test**: steps the fake clock and checks one rule.
- **Replay test**: feeds recorded readings back and compares the torque.
- **Property test**: throws many random inputs at one rule.
- **Golden trace**: a trusted recording from a healthy run.

## The Problem

You change a robot controller and want to know if it still works. Trying it on a real arm takes time and risks damage, and a test that only checks "it returns a number" passes even when the arm runs away.

## The Concept

A bug in robot code can break hardware, so it must be caught on a computer before the robot moves.

![Test kinds](../assets/diagram-test-kinds.png)

*Unit: step the fake clock, check one rule. Replay: compare torque on recorded readings. Property: random inputs, one rule.*

![Fake clock](../assets/diagram-fake-clock.png)

*The controller asks an object for the time: the real clock in production, a fake in tests.*

![Sign bug](../assets/fig-sign-bug.png)

*Left: the step test fails because the joint ends far from the target. Right: the buggy controller mirrors the recorded torque.*

Replay example. A step of 1.0 rad gives `kp * error = 40 * 1.0 = 40`, clipped to `tau_max` 10, so the recorded first torque is +10.0. The flipped controller answers -10.0 first, then the mirror of all 80 recorded samples, 10 ms apart. The replay test fails at the first.

![Replay](../assets/clip-example.mp4)

*The red arrow is torque: green pushes toward the target, blue (sign flipped) away.*

![Property torque](../assets/fig-property-torque.png)

*Property rule: torque is finite and never over the limit.*

## Build It

`FakeClock` has `now()` and `advance(dt)`. `MockJoint` raises on a torque over its limit, NaN (not a number) included. `Controller` is a PD loop that gives zero torque when updates stop for too long. `run()` returns `(q_meas, q_ref, tau)` rows.

```python
def test_step_direction_test_catches_the_sign_bug():
    with pytest.raises(AssertionError, match="moved away"):
        check_step_direction(polarity=-1)
```

`code/tests/golden_trace.json` came from the healthy controller. The controller returns zero torque for NaN and infinity, or the property test fails.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/04-testing-robot-code -q
python3 phases/15-safety-and-deployment/04-testing-robot-code/code/main.py
```

## Use It

In a ROS 2 node, inject the clock the same way. Replay real bags of a good run through new code before each release.

## Ship It

`outputs/skill-robot-test-plan.md` turns a controller into unit, replay and property tests.

## Exercises

1. Change `kp`. Does the replay test fail?
2. Write a property test that a stale controller returns exactly zero.
3. Test a swapped `q_meas` and `q_ref` argument order.
