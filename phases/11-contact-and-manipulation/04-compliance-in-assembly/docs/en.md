# Compliance in Assembly

> A peg jams when the tool is too stiff to give way, because the side force it creates feeds the friction that holds the peg.

**Type:** Build   **Prerequisites:** 11/01 Contact Models, 11/02 Force and Hybrid Control   **Time:** ~15 minutes

## In Plain Words

A tilted pencil can wedge in a snug holder. Holding its upper end rigidly to the side makes the pencil press hard against the walls.
Those walls push back, and their friction opposes the downward insertion.

Compliance lets the grip yield sideways, reducing the wall load so the pencil can straighten and slide deeper. The assembly model
checks whether the contact forces can balance the wrist's push and twist. If they can, the peg can stay jammed instead of moving.

## The Problem

A robot inserts a peg into a tight hole. With a fraction of a millimetre of misalignment the peg stops halfway, and pushing harder holds it more firmly.

## The Concept

![How a stiff wrist jams the peg](../assets/diagram-jam-chain.png)

*A stiff wrist turns a small offset into a large side force. It presses the tip on the wall, and friction grows until the contacts hold the peg.*

![A compliant wrist gives way](../assets/diagram-comply.png)

*A soft wrist makes a small side force, so the peg slides down and its tilt shrinks.*

The tilted peg has its tip on one wall and touches the hole edge on the other, so one number, the tip depth, fixes its pose. At each depth the wrist applies a wrench. The peg jams if forces inside the two friction cones can cancel it.

![Jam map over wrist stiffness and offset](../assets/fig-jam-map.png)

*Orange jams. A stiff wrist jams from about 0.7 mm of offset, while a wrist below about 2.5e3 N/m inserts for every offset shown.*

![Contact forces along the insertion](../assets/fig-contact-forces.png)

*The soft wrist keeps the tip force near the push. The stiff one starts with tens of newtons and jams where its side force changes sign.*

## Build It

Every depth gives a wrist wrench `wr` and the four cone-edge wrenches. It is a jam if `-wr` is a non-negative combination of three of them.

```python
A = edges[list(idx)].T
if abs(np.linalg.det(A)) > 1e-12 and (np.linalg.solve(A, -wr) >= -1e-9).all():
    return True
```

Assumptions: a zero-width peg, a sharp hole with no chamfer, quasi-static motion, contact only at the tip and the mouth edge. The wrist is a lateral spring `kx`, a torsion spring and a constant push, with Coulomb friction `mu`. The model starts already wedged, so landing on the edge is not covered.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/04-compliance-in-assembly -q
python3 phases/11-contact-and-manipulation/04-compliance-in-assembly/code/main.py
```

## Use It

Real cells use a remote center compliance device or software compliance. Compare your wrist's lateral stiffness with a jam map for your clearance and `mu`.

Sources: Wikipedia, "Remote center compliance" (opened 2026-11-09): a misaligned peg takes a side force and rotates until insertion stalls, and a compliant device corrects it.

## Ship It

`outputs/skill-assembly-compliance-check.md` reviews an insertion for jam risk before you tune the push force.

## Exercises

1. Find the largest `kx` that still inserts at `e = 1 mm`.
2. Raise `mu` from 0.1 to 0.6 and plot how the jam boundary moves.
3. Add a chamfer by starting the wedge at a smaller depth.
