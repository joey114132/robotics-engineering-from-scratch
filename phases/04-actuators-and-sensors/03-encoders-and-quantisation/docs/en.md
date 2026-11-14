# Encoders and Quantisation

> An encoder reports whole counts, so a slow joint reads as a jumpy velocity, and every filter that calms it makes it late.

**Type:** Build   **Prerequisites:** 04/01 Motor and Gearbox, 03/01 The Sampling Limit   **Time:** ~15 minutes

## In Plain Words

A slotted disc turns slowly past a fixed reader. The reader can only say that one more slot edge went by, which is one count. To estimate speed, you divide the counts by the time you counted for.

Check every millisecond and you usually see no edge, then suddenly one, so the speed reads zero and then far too high although the disc turns steadily. Wait longer between checks and the readings steady out, but each one describes a moment further back, so it follows speed changes late.

## The Problem

You raise the loop rate to make a joint feel smoother, and at slow speed the velocity signal gets worse. It jumps between zero and a large value, and the damping term `kd * velocity` (a brake that grows with speed) kicks the joint at every jump. A filter stops the kicks, but now the velocity arrives late and the joint oscillates.

## The Concept

The shaft angle is smooth, the counts are steps, and differencing (subtracting the previous count) turns each step into a spike.

![Shaft angle to velocity](../assets/diagram-encoder-pipeline.png)

*Smooth shaft, stepped counts, spiky velocity.*

One count is `2*pi / CPR` radians (CPR: counts per revolution). Dividing by the sample time `dt` gives the smallest non-zero speed a one-sample difference can report, `2*pi / (CPR * dt)` (the velocity step): 1.53 rad/s for `CPR = 4096` and `dt = 1 ms`. A joint at 0.1 rad/s makes a count only about every 15 ms, so 14 of every 15 readings are zero and the rest read 1.53. Their average is still right.

![Window length trade](../assets/diagram-window-tradeoff.png)

*Longer window: smaller steps, less noise, older estimate.*

A window of `n` samples (counts compared `n` samples apart) divides the step by `n` and delays a changing signal by `n*dt/2`, since it describes the window's middle.

In the lesson's lag test the speed rises at 2 rad/s^2 and `n = 20` at 1 kHz (`dt` = 1 ms). The estimate is 10 ms old, so it reads `2 * 0.01 = 0.02` rad/s too low.

![Two dials on a shaft that speeds up](../assets/clip-example.mp4)

*A very fine encoder leaves only the delay. The blue needle (one sample) sits on the true speed, the green one (20 samples) trails by 10 ms.*

![Velocity noise and delay against window](../assets/fig-encoder-velocity.png)

*Left: 1 kHz gives rare tall spikes, 100 Hz small steps. Right: noise falls with window length while delay grows linearly.*

## Build It

```python
def min_velocity_step(cpr, dt):
    return TWO_PI / cpr / dt

def window_velocity(c, cpr, dt, n):
    return (c[n:] - c[:-n]) * TWO_PI / cpr / (n * dt)

def window_lag(n, dt):
    return n * dt / 2
```

Tests check whole-step output, no bias, the noise `step * sqrt(d * (1 - d))` (`d`: fraction of readings with a count) and the lag `n*dt/2`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/03-encoders-and-quantisation -q
python3 phases/04-actuators-and-sensors/03-encoders-and-quantisation/code/figure.py
```

## Use It

Drives estimate speed by counting edges per window or timing the gap between edges, and the maxon page says counting struggles at very low speed. Compare the fixed window here with a period-based estimate on the same ramp.

Sources: [maxon, encoder selection part three](https://www.maxongroup.com/en-us/knowledge-and-support/blog/encoder-selection-part-three-speed-control-25728), accessed 2026-11-09.

## Ship It

`outputs/skill-encoder-velocity-check.md` computes the velocity step and picks a window for a joint.

## Exercises

1. Add a period-based estimate that times the gap between counts and compare its noise at 0.1 rad/s.
2. Find the speed above which a one-sample difference has less than 10% error.
3. Show that the dip near `n = 15` moves when the ramp speed changes.
