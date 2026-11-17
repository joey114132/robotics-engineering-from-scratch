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

Picture a robot pushing a peg into a tight hole, a millimetre or less out of line. The peg stops halfway, and pushing harder only holds it more firmly.

## The Concept

A real assembly robot is never perfectly aligned, so it must give way a little to get the part in.

A stiff wrist insists on its position, so a small misalignment turns into a big sideways force. That force presses the peg against the wall, and the wall's friction holds it. This is a jam.

![Chain](../assets/diagram-jam-chain.png)

*Stiff wrist: a big side force, and friction holds the peg.*

A soft wrist gives way sideways, called compliance. The side force stays small, and the peg straightens and slides down.

![Comply](../assets/diagram-comply.png)

*Soft wrist: a small side force, and the peg slides down.*

![Two wrists](../assets/clip-example.mp4)

*Blue jams halfway. Green goes in.*

![Jam map](../assets/fig-jam-map.png)

*Stiff wrists jam. Soft wrists insert.*

![Forces](../assets/fig-contact-forces.png)

*The stiff wrist starts with a big side force.*

Without friction the peg never jams.

<details><summary>The math (optional)</summary>

Stiffness `kx` is sideways force per metre of stretch, so the side force at the tip is about `kx` times the misalignment. With a 1 mm offset and a 5 N push, the tilted peg's top sits about 2.1 mm from the hole centre while the tool holds 1 mm, so the wrist stretches about 1.1 mm: 1e5 N/m gives 112 N sideways, 1e3 N/m gives 1.1 N and slides in. At 34.6 mm depth the forces in the two friction cones can balance the wrist's push and twist: the stiff peg locks. A jam means the negated wrist wrench is a non-negative mix of three of the four cone-edge wrenches. A stiff wrist jams from about 0.7 mm of offset; a wrist below about 2.5e3 N/m inserts for every offset shown.

</details>

## Build It

The code checks each depth for a jam.

```python
A = edges[list(idx)].T
if abs(np.linalg.det(A)) > 1e-12 and (np.linalg.solve(A, -wr) >= -1e-9).all():
    return True
```

Assumptions: zero-width peg, sharp hole, slow motion. Landing on the hole edge is not covered.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/04-compliance-in-assembly -q
python3 phases/11-contact-and-manipulation/04-compliance-in-assembly/code/main.py
```

## Use It

Real cells use a remote center compliance device or software compliance. Compare your wrist's stiffness with the jam map.

Sources: Wikipedia, "Remote center compliance" (opened 2026-11-09).

## Ship It

`outputs/skill-assembly-compliance-check.md` reviews an insertion for jam risk before you tune the push.

## Exercises

1. Find the stiffest wrist that still inserts a 1 mm offset.
2. Make the surfaces grippier; see the jam boundary move.
3. Add a bevelled hole edge and see whether it helps.
