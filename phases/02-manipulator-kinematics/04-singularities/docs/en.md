# Singularities and Damped Least Squares

> Learn why a nearly straight arm makes joints spin wildly, and the small trick that calms them.

**Type:** Build   **Prerequisites:** 02/03 The Jacobian   **Time:** ~15 minutes

## In Plain Words

A bench arm straightens its elbow to move the hand outward. Near full stretch the links line up, so an elbow turn moves the hand mostly sideways. The elbow must spin ever faster, and at full stretch no turn moves the hand outward.

That pose is a singularity, where a plain Jacobian inverse asks for a huge joint speed; damped least squares caps it.

## Key Terms

- **Singularity**: a pose where the arm loses a direction of tip motion, such as a fully straight arm.
- **Jacobian inverse**: the matrix that turns a wanted tip velocity back into joint speeds.
- **Determinant (`det J`)**: one number from a matrix that falls to 0 when the matrix loses a direction.
- **Manipulability**: a score, `sqrt(det(J J^T))`, for how freely the tip can move; it peaks at a right-angle elbow.
- **Singular value**: how much a matrix stretches one direction; a small one means a nearly lost direction.
- **Damped least squares**: an inverse that accepts a small error, set by `lam`, to keep joint speeds bounded.

## The Problem

You command a robot's hand straight outward at 0.1 m/s. Near full stretch the controller asks the elbow for a hundred radians per second, the drive hits its limit, and the tip leaves the path.

## The Concept

Real arms pass near poses where one direction of motion disappears.

![The chain of events](../assets/diagram-chain.png)

*A shrinking elbow angle shrinks `det J`; the inverse then asks for huge speeds.*

For this arm `det J = L1 L2 sin q2`, so the arm is singular when fully straight or fully folded (Craig, Ch. 5, Sec. 5.8). Then no joint speeds move the tip along the arm.

Each column of `J` is where the tip goes when one joint turns. At `q2 = 1.4` rad `det J = 0.5 * 0.4 * sin 1.4 = 0.20`; at `q2 = 0` the columns are parallel and `det J = 0`.

![Two arrows merge](../assets/clip-example.mp4)

*The two columns of `J`: tip velocity per unit speed of shoulder (amber) and elbow (dark blue).*

Damped least squares adds `lam^2 I` (`I` is the identity matrix) inside the inverse.

![Damped least squares](../assets/diagram-damping.png)

*Speed can no longer exceed `|v| / (2 lam)`.*

![Joint speed and tip error](../assets/fig-speed-blowup.png)

*Solid lam = 0.05, dashed 0.15. Left: the plain inverse grows like `1 / q2`; damped ones stay under dotted bounds. Right: damped ones lag.*

## Build It

```python
def solve(J, v, lam):
    if lam == 0.0: return np.linalg.solve(J, v)            # plain inverse
    return J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(len(v)), v)
```

Each singular value `s` of `J` becomes `s / (s^2 + lam^2)`, never above `1 / (2 lam)`. Small `lam` tracks closely but moves fast; large `lam` lags.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/04-singularities -q
python3 phases/02-manipulator-kinematics/04-singularities/code/main.py
```

## Use It

Libraries compute pseudo-inverses with a cutoff on small singular values; compare with `solve` near `q2 = 0.01`.

## Ship It

`outputs/skill-singularity-guard.md` guards a velocity controller with a manipulability monitor.

## Exercises

1. Grow `lam` only when `manipulability(J)` falls below a threshold.
2. Find the smallest `lam` that keeps joint speed below 2 rad/s at `q2 = 0.01`.
3. Show a path through the folded pose has the same trouble.
