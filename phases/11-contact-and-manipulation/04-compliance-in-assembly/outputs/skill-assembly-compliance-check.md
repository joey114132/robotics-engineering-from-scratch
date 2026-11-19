---
name: assembly-compliance-check
description: Use when a peg, screw, connector or press fit stops partway during robotic insertion, or when choosing wrist or tool compliance for a tight fit. Checks jam risk from clearance, friction, lateral stiffness and misalignment.
---

# Assembly compliance check

1. Record the clearance, the friction coefficient, the expected lateral misalignment and tilt, and the stiffness of the wrist or tool in the lateral and rotation directions.
2. Find the lean the wrist alone would give the peg while only the tip touches (where its twist balances), and the most lean the hole allows at each depth: the clearance divided by the depth. The depth where the hole allows less than the wrist wants is where the edge catches the peg.
3. From there check the two-contact wedge: with the tip on one wall and the edge on the other, can the friction cones balance the wrench the wrist applies? If yes at any depth, the insertion will stall there. A side force that grows with depth is the warning.
4. Prefer more lateral compliance, a chamfer, or a smaller misalignment, in that order of cost. Do not count on a larger push force: re-run the check at the new push before trusting it.
5. State the assumptions that limit the answer: peg width, chamfer, friction value and whether the entry phase was checked.

Return the largest lateral stiffness that inserts for the stated misalignment, the depth of the first jam if any, and which assumption is least certain. Never change the cell.
