# Contact Models

> A block sticks on a tilted plane exactly when tan(theta) is at most mu, because friction can only push inside its cone.

**Type:** Build   **Prerequisites:** 03/02 Gravity Compensation   **Time:** ~15 minutes

## In Plain Words

Place an eraser on a textbook and slowly tilt the book. Gravity pulls the eraser downhill, and friction from the book pulls it back uphill. Tilting more raises the downhill pull and lowers the force pressing the eraser into the book.

Friction has a cap: at most `mu` times the pressing force, where `mu` says how grippy the surfaces are. All the friction forces up to that cap form the friction cone. Once the friction needed to hold the eraser passes the cap, the eraser slides.

## The Problem

Your gripper holds a part, you tilt the wrist a few degrees, and the part slides out. Held a little flatter, it would have stayed. A rigid-body simulator gets it right only if its contact model has the same switch between sticking and sliding.

## The Concept

Call the tilt `theta`, the mass `m` and gravity `g`. Gravity splits into `fn = m g cos(theta)`, which presses the block into the plane (the normal force), and `m g sin(theta)`, which pulls it down the slope. To stay put the block needs friction `ft = m g sin(theta)` along the slope, so `ft / fn = tan(theta)`. The friction cone allows `ft / fn` up to `mu`.

![Two layers of a simulated contact](../assets/diagram-penalty-layers.png)

*In a simulator the block sinks a hair into the plane. That penetration gives the normal force, which sets the cap on friction. A sideways spring holds the contact still until it hits the cap.*

Take `mu = 0.5`. A 25 degree ramp needs 0.47 and holds. A 35 degree ramp needs 0.70, so the block slides: friction stays at its cap `mu * fn`, leaving a net pull of `m g (sin(theta) - mu cos(theta))`, about 1.6 m/s² here.

![A tilting plank](../assets/clip-example.mp4)

*Watch the orange block as the plank tilts. It holds until the plank passes the see-through marker at 26.6 degrees, then slides.*

![Stick or slip decision on a tilted plane](../assets/diagram-stick-slip.png)

*The only question is whether the needed friction fits inside the cone.*

![Force trajectories in the friction cone and slip acceleration against tan(theta)](../assets/fig-stick-slip.png)

*Left: the sticking blocks end inside the cone, the sliding block rides its edge. Right: simulated acceleration is zero until tan(theta) passes mu, then rises as derived above.*

## Build It

Normal force is a spring-damper on penetration that never pulls. Friction is a tangential spring to an anchor, clipped at `mu * fn`. When it clips, the anchor is dragged along.

```python
fn = max(K * pen - C * nv, 0.0)
ft = -KT * (s - anchor) - CT * v
if abs(ft) > mu * fn:
    ft = np.sign(ft) * mu * fn
    anchor = s + ft / KT
```

Assumptions: a point block, one contact, a planar slope, fixed spring constants, semi-implicit Euler at 0.1 ms. The block starts touching the plane at rest.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/01-contact-models -q
python3 phases/11-contact-and-manipulation/01-contact-models/code/main.py
```

## Use It

MuJoCo uses the same two ideas: a soft normal force and a friction cone that its docs say can be elliptic or pyramidal. Build the same tilted block there and compare its sliding angle with `arctan(mu)`.

Sources: MuJoCo documentation, Computation chapter (opened 2026-11-09).

## Ship It

`outputs/skill-contact-model-check.md` checks a contact setup for a stick/slip surprise before you blame the controller.

## Exercises

1. Raise `K` by 10 times and check that the sticking angle does not move but the settling time does.
2. Make `mu` differ for static and sliding contact and find the angle where the block starts and keeps moving.
3. Add a horizontal push on the block and find the push at which it begins to slide up the slope.
