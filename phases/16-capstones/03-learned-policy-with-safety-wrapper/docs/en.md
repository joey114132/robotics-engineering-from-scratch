# A Learned Policy with a Safety Wrapper

> A learned policy is allowed to be wrong sometimes, so the code around it must make sure that being wrong is never dangerous.

**Type:** Build   **Prerequisites:** 03/01 The Sampling Limit, 03/04 PID and Tuning   **Time:** ~30 minutes

## The Problem

A policy trained from demonstrations works in every test, then one bad network output or one lost camera frame sends a joint into its limit. Nobody can prove a learned model never does this. What you can do is put a small piece of plain code between the model and the motor, and prove that piece.

## The Concept

![Learned policy inside a safety wrapper](../assets/diagram-policy-system.png)

*Demonstrations train a nearest-neighbour policy. Its action passes through a wrapper before it reaches the joint, and the wrapper also sees how old the observation is.*

![Two faults, one wrapper](../assets/diagram-policy-broken.png)

*A spike is clipped and rate limited. A lost observation becomes a hold command once it is too old.*

![The task succeeding](../assets/fig-policy-result.png)

*On a clean run the cloned policy follows the expert to the target. The wrapper only slows the first torque ramp.*

![Faults with and without the wrapper](../assets/fig-policy-faults.png)

*Spike: peak torque 40 Nm without the wrapper, 3 Nm with it, and the joint peaks at 1.36 rad against 1.01 rad. Lost observation: 1.47 rad against 1.01 rad. The limit is 1.3 rad.*

## Build It

The wrapper is three rules in a fixed order. It holds if the observation is stale, clips to the torque limit, then limits the change per step.

```python
if age > self.max_age: raw = 0.0
c = np.clip(raw, -self.umax, self.umax)
r = self.u + np.clip(c - self.u, -self.du, self.du)
```

Each rule counts how often it changed the action. Counts are the evidence. The spike run shows 1 clip, the lost-observation run shows 23 hold steps, and a clean run shows no clip and no hold.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/16-capstones/03-learned-policy-with-safety-wrapper -q
python3 phases/16-capstones/03-learned-policy-with-safety-wrapper/code/main.py
```

## Use It

ros2_control provides joint-limit handling for hardware interfaces, and the `enforce_command_limits` parameter on `ros2_control_node` sets joint-limit handling globally for all interfaces. At startup the controller manager logs which limits each joint has. Compare them with the three rules here.

Sources: [ros2_control joint limiting](https://control.ros.org/rolling/doc/ros2_control/hardware_interface/doc/joint_limiting.html), read 2026-11-09.

## Ship It

`outputs/skill-policy-wrapper-audit.md` checks that a wrapper around a learned policy covers range, rate and staleness.

## Exercises

1. Raise `max_age` until the lost-observation run first crosses 1.3 rad.
2. Add a speed limit as a fourth rule and count its interventions.
3. Train on 5 episodes instead of 40 and see which fault the wrapper now catches more often.
