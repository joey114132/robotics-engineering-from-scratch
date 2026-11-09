# Latency Budget

> Every stage of the loop adds delay, delay spends phase margin, and what is left decides how large kd may be.

**Type:** Build   **Prerequisites:** 04/03 Encoders and Quantisation, 03/01 The Sampling Limit   **Time:** ~15 minutes

## The Problem

A joint is stable on the bench with `kd = 8` and starts to buzz once it is on the real controller. Nothing in the gains changed. What changed is that the command now takes a few milliseconds to travel from the sensor to the drive, and nobody added those milliseconds up.

## The Concept

![Latency budget](../assets/diagram-latency-budget.png)

*Each stage delays the signal and the delays add. A held command also lags by half a period.*

For a PD loop on an inertia `J`, the gain crossover `wc` solves `J^2 wc^4 = kd^2 wc^2 + kp^2`. A delay `T` adds lag `wc*T` and leaves the gain alone, so the phase margin falls to `PM - wc*T`. The delay margin is `PM / wc`.

![Delay spends the phase margin](../assets/diagram-delay-margin.png)

*Delay lowers the margin until it reaches zero, and the fix is a lower crossover.*

A larger `kd` raises `wc` faster than it raises `PM`, so past a point the delay margin shrinks. Given a loop delay, there is a largest `kd` that still works.

![Delay margin against kd and simulated responses](../assets/fig-latency-margin.png)

*Left: the 5.5 ms budget rules out kd above about 14, and also very small kd. Right: a delay of 0.6 times the margin settles, 1.5 times grows.*

## Build It

```python
def crossover(kp, kd, J):
    return np.sqrt((kd**2 + np.sqrt(kd**4 + 4 * J**2 * kp**2)) / (2 * J**2))

def phase_margin(kp, kd, J, delay=0.0):
    wc = crossover(kp, kd, J)
    return np.arctan(kd * wc / kp) - wc * delay

def delay_margin(kp, kd, J):
    return phase_margin(kp, kd, J) / crossover(kp, kd, J)
```

`simulate()` runs the delayed loop. Tests check the crossover against a numeric gain of one, and that the simulation is stable at 0.6 and unstable at 1.5 times `delay_margin()`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/04-latency-budget -q
python3 phases/04-actuators-and-sensors/04-latency-budget/code/figure.py
```

## Use It

Delay margin is a phase-margin reading on a Bode plot divided by the crossover frequency, as derived in this lesson. Compare your result with a frequency-response tool such as `scipy.signal` or a MATLAB-style Bode plot of the same loop.

## Ship It

`outputs/skill-latency-budget-check.md` sums a loop's delays and returns the largest safe `kd`.

## Exercises

1. Add a first-order filter to the loop and recompute the margin numerically.
2. Find the delay margin as `kp` doubles at fixed `kd`.
3. Move the filter delay from 2 ms to 1 ms and report the new largest `kd`.
