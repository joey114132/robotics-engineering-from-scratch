# Imitation from Demonstrations

> If you cannot write the reward, show the robot what to do and fit a function to the examples.

**Type:** Build   **Prerequisites:** 03/02 Gravity Compensation   **Time:** ~15 minutes

## In Plain Words

Watch a friend weave between playground cones, recording where they stand and which way they move next. Those paired examples can teach
a rule for choosing a movement at your current position.

Imitation learning fits that rule without needing a reward for every move. Nearby examples can preserve a local swerve, while a single
linear rule can average different detours into a straight route through a cone. More demonstrations help only if the fit can express
the behaviour.

## The Problem

You can drive a robot around an obstacle by hand, but writing a controller that does it for every start position takes days. Writing a reward for a learning algorithm is no easier. Recording a few good runs and training on them is cheap. That leaves two questions: how many runs you need, and what kind of function to fit.

## The Concept

![From expert to policy](../assets/diagram-imitation-pipeline.png)

*An expert acts. You store each observation with the action taken, and a regression turns those pairs into a policy.*

This is supervised learning where the label is the expert's action. The state is a point `x` in the plane, the action is a velocity, and the expert pulls toward the goal while swerving around a disc.

![Two ways to fit the same data](../assets/diagram-imitation-fits.png)

*A straight line averages "go left" and "go right" into "go straight". Nearest neighbours copy one side.*

![Success against number of demonstrations, and rollouts](../assets/fig-imitation-success.png)

*Left: nearest neighbours reach expert success after about a dozen demonstrations, while least squares gets worse. Right: the linear policy goes straight through the disc.*

## Build It

The expert adds a swirl term near the obstacle, then the code collects pairs and fits two policies.

```python
X, A = collect(rng, n_demos)        # stacked (position, velocity) pairs
policy = fit_knn(X, A, k=3)         # mean action of the 3 closest demo states
W = np.linalg.lstsq(feats, A)[0]    # or one linear rule, fit_linear
```

`success()` counts a rollout only if it never enters the obstacle and ends within 0.1 m of the goal. Run it with:

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/01-imitation-from-demonstrations -q
python3 phases/13-learning-for-robots/01-imitation-from-demonstrations/code/figure.py
```

## Use It

The test file cross-checks the neighbour search against `scipy.spatial.cKDTree` and skips if SciPy is missing. Production code replaces both fits with a neural network. The data pipeline stays the same, and the number of demonstrations is still the first thing to vary.

Sources: Ross, Gordon and Bagnell, "A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning", arXiv:1011.0686 (opened 2026-11-09; its abstract says sequential prediction violates the i.i.d. assumption of statistical learning).

## Ship It

`outputs/skill-imitation-data-check.md` is a checklist for judging a demonstration set before training.

## Exercises

1. Add a second obstacle and find how many demonstrations 3-NN needs to reach 95% success.
2. Replace `k=3` by `k=1` and `k=15` and explain the change in success.
3. Give the observation a velocity term and check that least squares still fails.
