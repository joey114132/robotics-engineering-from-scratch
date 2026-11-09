# A Safety Wrapper for Learned Policies

> A learned policy is a producer that can say anything. The layer after it must be deterministic and must not care what was said.

**Type:** Build   **Prerequisites:** 13/02 Behaviour Cloning Pitfalls   **Time:** ~15 minutes

## The Problem

A policy trained on demonstrations produces a command every tick, and nothing in training promised that the command is finite, small, smooth or based on a recent observation. One spike, one NaN or one frozen camera frame reaches the actuator at full speed. You cannot test a neural network into safety, but you can test a short deterministic layer.

## The Concept

![Wrapper pipeline](../assets/diagram-wrapper-pipeline.png)

*The wrapper checks the observation's age and runs the policy only on a usable one. It clips and rate-limits the output before anything moves, and logs each change.*

The policy may differ run to run. The wrapper does not, because the same inputs always give the same output and the same log. That is what makes it testable with ordinary asserts and fuzzing.

![Hold then fall back](../assets/diagram-wrapper-ladder.png)

*A short gap holds the last command. A gap past the deadline ramps to the fallback.*

![Raw against wrapped commands](../assets/fig-wrapper-containment.png)

*A point should go from x = 1 to 0. Without the wrapper a sign-flipped burst throws it to x of about 3.3. With it, x never exceeds 1, and the log counts 45 interventions.*

## Build It

`act()` runs these steps in order: reject a stale or missing observation, call the policy, replace a non-finite value, clip, and limit the change.

```python
raw = policy(obs)
target = fallback if not np.isfinite(raw) else float(np.clip(raw, lo, hi))
out = float(np.clip(target, last_out - max_step, last_out + max_step))
```

The fuzz test sends 2000 random commands, including NaN and infinity, and asserts every output obeys both limits.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/04-learned-policy-safety-wrapper -q
python3 phases/13-learning-for-robots/04-learned-policy-safety-wrapper/code/figure.py
```

## Use It

Real controllers already ship limiters. The ROS 2 `joint_limits` package, for example, provides interfaces for joint limits in controllers or hardware and a saturation limiter for position, velocity and acceleration. Put the wrapper's age check and log in front of it, not instead of it.

Sources: ROS Index, `joint_limits` package page (index.ros.org/p/joint_limits), opened 2026-11-09.

## Ship It

`outputs/skill-policy-safety-wrapper.md` is a review checklist for the layer between a learned policy and the actuator.

## Exercises

1. Add a velocity-dependent limit and write the fuzz test for it.
2. Make the fallback ramp to zero in `n` ticks and check that `n` matches the stopping distance.
3. Replay a recorded policy log through `Wrapper.act` and list the first intervention.
