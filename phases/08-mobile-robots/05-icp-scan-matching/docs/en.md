# Scan Matching with ICP

> To line up two scans, guess that each point's partner is its nearest neighbour, fit one rigid move, and repeat until the error stops falling.

**Type:** Build   **Prerequisites:** 01/01 Rotations and SE(3), 08/01 Differential Drive and Odometry   **Time:** ~15 minutes

## In Plain Words

Lay a dotted outline on tracing paper over another copy. Pair each dot with the nearest dot underneath, then slide and turn the whole
sheet to bring those pairs closer. Repeat the pairing after each move.

ICP aligns scans this way without knowing which points match. A small starting offset helps it find the right pairs. Starting far away
can pair the wrong features, so the dots get closer while the estimated movement is still wrong.

## The Problem

Wheel odometry (08/01) drifts, and a laser scanner sees the same room twice from two slightly different poses. You want the move between the two scans so you can correct the pose. A program needs a rule that works on raw points with no labels.

## The Concept

![ICP: guess the pairs, fit, repeat](../assets/diagram-icp-loop.png)

*Each pass pairs points, fits one rigid move to those pairs, and applies it.*

If the pairs were right, the best rotation `R` and shift `t` would come in one step. For paired points the SVD of the cross-covariance of the centred clouds gives `R`, and a sign fix on the last singular direction forbids a mirror image. The shift is then `t = q_mean - R p_mean`. ICP does not know the pairs, so it uses the nearest point as a guess.

![Why a big start offset ends in a wrong answer](../assets/diagram-icp-failure.png)

*If the scans start further apart than the point spacing, nearest points are wrong partners and the fit locks in the wrong answer.*

The error never rises, because each fit is optimal for its pairs and re-pairing only shortens distances.

![ICP in four views](../assets/fig-icp-basin.png)

*Three panels show one run converging. The last shows final pose error against starting rotation: good up to about 65 to 70 degrees for this room, then a local minimum. The dashed line is the 0.05 m point spacing.*

On this demo, the residual floor is about the point spacing. This is not universal: different samples can align exactly, and tiny residuals can hide a wrong pose. A single straight wall poorly constrains sliding along it.

## Build It

```python
def kabsch(P, Q):
    pc, qc = P.mean(0), Q.mean(0)
    U, _, Vt = np.linalg.svd((P - pc).T @ (Q - qc))
    D = np.diag([1.0, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, qc - R @ pc

match = dst[nearest(cur, dst)]
dR, dt = kabsch(cur, match)
cur = cur @ dR.T + dt
```

`icp()` repeats this and returns the total `R`, `t` and the error history.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/05-icp-scan-matching -q
python3 phases/08-mobile-robots/05-icp-scan-matching/code/main.py
```

## Use It

Open3D's ICP registration takes an initial transformation that roughly aligns the clouds, and iterates between finding correspondences and updating the transformation. Compare it with `icp()` and feed it your odometry as the initial guess.

Sources: Open3D ICP registration tutorial, https://www.open3d.org/docs/latest/tutorial/pipelines/icp_registration.html (opened 2026-11-10).

## Ship It

`outputs/skill-icp-check.md` audits a scan-matching step for bad starts, flat walls and false confidence.

## Exercises

1. Add 2 cm of noise to both scans and measure the pose error against the spacing.
2. Start ICP from the odometry guess and find the largest rotation drift it still repairs.
3. Add a trimmed fit that ignores the worst 20% of pairs and test it with a missing corner.
