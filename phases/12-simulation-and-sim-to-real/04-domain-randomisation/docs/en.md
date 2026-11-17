# Domain Randomisation

> Learn how to tune a robot's controller so it works on many slightly different robots, not just one.

**Type:** Build   **Prerequisites:** 12/03 System Identification   **Time:** ~15 minutes

## In Plain Words

Arms leave the same assembly line, yet no two are alike. Gains tuned on the average arm leave no margin, so some copies overshoot.

Domain randomisation tunes the gains across many different simulated arms. A narrow range misses real differences. A wide range gives slow, cautious gains.

## Key Terms

- **Domain randomisation**: tuning a controller across many simulated robots whose numbers are randomly changed.
- **Nominal plant**: the simulated arm with the plain, average numbers.
- **PD controller**: pushes toward the target by how far off it is, and brakes by how fast it moves.
- **Gains**: the two numbers that set how hard the controller pushes and brakes.
- **Width (`w`)**: how far each number may be changed, as a fraction.
- **Settling**: staying close to the target.

## The Problem

Your controller works on the simulated arm and fails on the real one, which is a bit heavier, stickier and slower. Randomising the simulator can cover that, but how wide?

## The Concept

No two real robots are identical, so tuning on one perfect copy is a gamble. Instead we tune on many simulated arms whose weight, friction and delay are randomly changed. Too narrow a range misses real differences. Too wide gives slow, cautious gains.

![Test loop](../assets/diagram-dr-loop.png)

*Change every number a little, run the same controller on each arm, and count how many succeed.*

![Widths](../assets/diagram-dr-widths.png)

*Too narrow is brittle, the right width is reliable and fast, too wide is slow and over-cautious.*

![Width sweep](../assets/fig-dr-width.png)

*Left: gains tuned on the average arm often fail on real arms, gains tuned on many arms rarely do. Right: tuning wider than needed costs speed.*

![Same 12 arms](../assets/clip-example.mp4)

*Lamps light as arms settle. The green set, tuned on the right width, settles first.*

<details><summary>The math (optional)</summary>

Each number is scaled by `1 +- w`. A PD controller with a torque limit and sensor delay steps a joint by 1 rad. It succeeds if it settles within 0.05 rad by 0.8 s and peaks below 1.05 rad. A failure costs 2 s. `tune()` keeps the `kp`, `kd` pair with the lowest mean cost. At width 0.3 inertia 0.05 becomes anything from 0.035 to 0.065. Over 12 such arms, nominal-tuned gains (`kp` 4.5, `kd` 0.70) leave 6 failing and drop to 57% success. Gains tuned across 0.3 (`kp` 7.7, `kd` 1.35) reach 99% and settle in 0.52 s on average. Gains tuned across 0.6 (`kp` 4.5, `kd` 0.88) settle all 12 but need 0.59 s, about 10% slower.

</details>

## Build It

`simulate()` runs many arms at once. `tune()` tries every pair of gains on the same random arms and keeps the best.

```python
def sample(width, n, rng):
    return {k: v * (1 + width * rng.uniform(-1, 1, n)) for k, v in NOM.items()}
```

Width 0 gives the average arm. Tests check that an arm simulated alone matches the same arm in a batch.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/12-simulation-and-sim-to-real/04-domain-randomisation -q
python3 phases/12-simulation-and-sim-to-real/04-domain-randomisation/code/main.py
```

## Use It

In MuJoCo you can scale an arm's mass, damping and friction before each run.

Sources: MuJoCo 3.11.0 Python bindings (2026-11-09).

## Ship It

`outputs/skill-randomisation-range.md` picks and checks a randomisation range.

## Exercises

1. Randomise only the delay. Which number matters most?
2. Lower the real width to 0.15. What tuning width is best?
3. Score the worst arm instead of the average.
