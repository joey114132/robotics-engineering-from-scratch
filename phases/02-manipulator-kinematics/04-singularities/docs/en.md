# Singularities and Damped Least Squares

> When the arm straightens, one direction of tip motion disappears, and the plain inverse answers with a joint speed that grows without limit.

**Type:** Build   **Prerequisites:** 02/03 The Jacobian   **Time:** ~15 minutes

## In Plain Words

With your shoulder fixed, a bent arm can move its fingertip outward by straightening. Near full stretch, much
more joint motion is needed for the same outward tip speed. At full stretch, joint rotations give no
instantaneous outward velocity.

That is a singularity. Inverting the Jacobian nearby asks for huge joint speeds. Damped least squares limits
that amplification, allowing some tip-speed error instead of demanding an impossible motion. More damping
lowers joint speeds but leaves more tip-speed error.

## The Problem

You command the tip to move straight outward at 0.1 m/s. As the arm nears full stretch, the controller asks the elbow for a hundred radians per second, the drive saturates, and the tip leaves the path. Nothing is broken. The Jacobian lost a direction and the controller still tried to invert it.

## The Concept

![The chain of events](../assets/diagram-chain.png)

*A shrinking elbow angle shrinks `det J`. A tip direction is lost, and the inverse asks for huge speeds.*

For this arm `det J = L1 L2 sin q2`, so the arm is singular when fully straight or fully folded (Craig, Ch. 5, Sec. 5.8). The manipulability `sqrt(det(J J^T))` is largest at a right-angle elbow. At a singularity `J` has rank one: no joint speeds make the tip move radially.

![Damped least squares](../assets/diagram-damping.png)

*Damped least squares adds `lam^2 I` inside the inverse. The speed can no longer exceed `|v| / (2 lam)`.*

![Joint speed and tip error](../assets/fig-speed-blowup.png)

*Left: the plain inverse grows like `1 / q2`, the damped solutions stay below their bounds. Right: the damped solutions stop following the command near the singularity.*

## Build It

```python
def solve(J, v, lam):
    if lam == 0.0: return np.linalg.solve(J, v)            # plain inverse
    return J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(len(v)), v)
```

Each singular value `s` of `J` is mapped to `s / (s^2 + lam^2)`, which never exceeds `1 / (2 lam)`. That is the bound the tests check. Choose `lam` as a trade: small `lam` follows the command closely and moves fast, large `lam` moves slowly and lags.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/04-singularities -q
python3 phases/02-manipulator-kinematics/04-singularities/code/main.py
```

## Use It

Libraries compute pseudo-inverses with a cutoff on small singular values. Compare their output to `solve` near `q2 = 0.01`, and read how they choose the cutoff or the damping.

## Ship It

`outputs/skill-singularity-guard.md` is a checklist for putting a manipulability monitor and a damped solver in front of a velocity controller.

## Exercises

1. Make `lam` grow only when `manipulability(J)` falls below a threshold.
2. Find the smallest `lam` that keeps joint speed below 2 rad/s at `q2 = 0.01`.
3. Show that a path through the folded pose has the same trouble as one through the stretched pose.
