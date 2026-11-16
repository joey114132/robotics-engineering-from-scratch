# Compliance in Assembly

> Learn why a stiff robot jams a peg in a tight hole, and why a gentler wrist slides it in.

**Type:** Build   **Prerequisites:** 11/01 Contact Models, 11/02 Force and Hybrid Control   **Time:** ~15 minutes

## In Plain Words

A robot arm pushes a thin peg into a tight hole, starting a little off to one side. A rigid wrist fights the offset, shoving the peg sideways into the walls, and their friction resists the downward push.

A wrist that gives way sideways, called compliance, lets the peg straighten and slide in.

## Key Terms

- **Compliance**: the ability to give way under a force instead of holding a position rigidly.
- **Jam**: the peg stops and pushing harder only holds it more firmly.
- **Stiffness (`kx`)**: the sideways force per metre the wrist is stretched.
- **Wrench**: a push and a twist packed together.
- **Chamfer**: a bevelled hole edge that guides the peg in.
- **Quasi-static**: moving so slowly that speeds and inertia can be ignored.

## The Problem

Picture a robot pushing a peg into a tight hole, misaligned by a millimetre or less. The peg stops halfway; pushing harder holds it more firmly.

## The Concept

A real assembly robot is never perfectly aligned, so it must give way a little.

![Chain](../assets/diagram-jam-chain.png)

*A stiff wrist turns a small offset into a large side force, and friction holds the peg.*

![Comply](../assets/diagram-comply.png)

*A soft wrist makes a small side force; the peg slides down.*

With a 1 mm offset and a 5 N push, the tilted peg's top sits about 2.1 mm from the hole centre while the tool holds 1 mm, so the wrist stretches about 1.1 mm: 1e5 N/m gives 112 N sideways, 1e3 N/m gives 1.1 N and slides in. At 34.6 mm depth the forces in the two friction cones cancel the wrist's push and twist: the stiff peg locks.

![Two wrists](../assets/clip-example.mp4)

*Red arrow: sideways push. Blue stops at 34.6 mm, green goes in.*

![Jam map](../assets/fig-jam-map.png)

*Orange jams: stiff wrists from about 0.7 mm of offset; wrists below about 2.5e3 N/m never.*

![Forces](../assets/fig-contact-forces.png)

*Soft: tip force near the push. Stiff: tens of newtons, jamming where side force changes sign.*

## Build It

Jam if `-wr`, the negated wrist wrench, is a non-negative mix of three of the four cone-edge wrenches.

```python
A = edges[list(idx)].T
if abs(np.linalg.det(A)) > 1e-12 and (np.linalg.solve(A, -wr) >= -1e-9).all():
    return True
```

Assumptions: zero-width peg, sharp hole, quasi-static, contact at the tip and the mouth edge only; the wrist is a lateral spring `kx`, a torsion spring and a constant push; Coulomb `mu`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/04-compliance-in-assembly -q
python3 phases/11-contact-and-manipulation/04-compliance-in-assembly/code/main.py
```

## Use It

Real cells use a remote center compliance device or software compliance. Compare your wrist's `kx` with a jam map.

Sources: Wikipedia, "Remote center compliance" (opened 2026-11-09): a misaligned peg stalls under side force; a compliant device corrects it.

## Ship It

`outputs/skill-assembly-compliance-check.md` reviews an insertion for jam risk before you tune the push.

## Exercises

1. Find the largest `kx` that still inserts at `e = 1 mm`.
2. Raise `mu` from 0.1 to 0.6; plot the jam boundary.
3. Add a chamfer: start the wedge shallower.
