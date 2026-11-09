---
name: assembly-compliance-check
description: Use when a peg, screw, connector or press fit stops partway during robotic insertion, or when choosing wrist or tool compliance for a tight fit. Checks jam risk from clearance, friction, lateral stiffness and misalignment.
---

# Assembly compliance check

1. Record the clearance, the friction coefficient, the expected lateral misalignment and tilt, and the stiffness of the wrist or tool in the lateral and rotation directions.
2. Estimate the side force at the tip as lateral stiffness times the misalignment. Compare it with the push force. A side force several times the push force is the jam signature.
3. Check the two-contact wedge: with the tip on one wall and the edge on the other, can the friction cones balance the wrench the wrist applies? If yes at any depth, the insertion will stall there.
4. Prefer more lateral compliance, a chamfer, or a smaller misalignment, in that order of cost. Raising the push force makes a jam firmer.
5. State the assumptions that limit the answer: peg width, chamfer, friction value and whether the entry phase was checked.

Return the largest lateral stiffness that inserts for the stated misalignment, the depth of the first jam if any, and which assumption is least certain. Never change the cell.
