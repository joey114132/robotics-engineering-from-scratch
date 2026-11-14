# Behaviour Cloning Pitfalls

> A cloned policy is accurate where the expert drove and wrong one step later, because its own mistakes put it somewhere the expert never was.

**Type:** Build   **Prerequisites:** 13/01 Imitation from Demonstrations   **Time:** ~15 minutes

## In Plain Words

A rover learns to drive round a pillar from clean runs with no bumps. One bump on a wheel pushes it to a spot none of those runs visited, where its steering is a poor guess. The next guess is worse again, so the error grows.

DAgger (dataset aggregation) lets the rover drive first. The expert then says what to do at the spots the rover actually reached, and those recovery examples go into the data before the rover learns again.

## The Problem

Your cloned policy scores well on held-out demonstrations (kept aside for testing), yet on the robot it drifts off the path and fails. Its training loss, the gap between its actions and the expert's, is measured only at demonstration spots, never at the states it creates itself.

## The Concept

![Errors feed on themselves](../assets/diagram-drift-loop.png)

*One wrong action puts the next observation outside the demonstrations, where the policy is worse, so the next error is larger.*

Noise added to the commanded velocity mimics wheel slip and delay. With four clean demonstrations the cloned policy, the learner, leaves the demonstrated states within a few steps, and its action error, the gap between its action and the expert's at that spot, climbs and stays high.

![DAgger loop](../assets/diagram-dagger-loop.png)

*Follow the numbers. One DAgger round: the learner drives, the expert labels the states it actually visited, those pairs join the data, and the learner refits.*

![Error over steps and success over rounds](../assets/fig-cloning-drift.png)

*Left: plain cloning error rises about sevenfold over the first 60 steps, and the policy after four DAgger rounds stays near zero. Right: success under noise climbs to the expert's level in about two rounds.*

Both rovers below learned from four demonstrations. The blue one, cloned plainly, starts 0.09 m from the nearest recorded state and is 0.31 m away when it hits the pillar; the green one, after four DAgger rounds, never exceeds 0.09 m. Over many starts, `python3 code/main.py` gives goal success of 52.5% for plain cloning, 90% after two rounds and 93% after four.

![Two rovers with lines to the nearest recorded state](../assets/clip-example.mp4)

*Watch the amber line from each rover to its nearest recorded state. Blue's keeps growing until the pillar. Green dots are states the learner visited and the expert labelled, so green's stays short.*

## Build It

`dagger()` is plain cloning when `rounds=0`. Each round adds labelled recovery states.

```python
for _ in range(rounds):
    V = np.vstack([rollout(pol, x0, rng)[:-1] for x0 in starts(rng, 5)])
    X, A = np.vstack([X, V]), np.vstack([A, [expert(x) for x in V]])
    pol = fit_knn(X, A)
```

The labels come from `expert(x)`, never from the learner. `drift_curves()` returns action error and distance to the nearest data state at every step.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/02-behaviour-cloning-pitfalls -q
python3 phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/code/figure.py
```

## Use It

The expert is often unavailable while the robot drives, so a person or planner must label states afterwards. Cheaper: record recovery moves on purpose. Either way, measure error on the learner's rollouts, not on held-out demonstrations.

Sources: Ross, Gordon and Bagnell, arXiv:1011.0686, opened 2026-11-09. It says a supervised learner can make as many as T² mistakes over T steps under its own state distribution, and defines DAgger as aggregating datasets over iterations.

## Ship It

`outputs/skill-cloning-drift-audit.md` is a procedure for finding compounding error.

## Exercises

1. Plot `dist` from `drift_curves` for plain cloning and say when the learner leaves the data.
2. Halve `NOISE` and find the smallest number of rounds that matches the expert.
3. Roll out a mix of expert and learner with the expert share decaying each round, like the paper's `beta`.
