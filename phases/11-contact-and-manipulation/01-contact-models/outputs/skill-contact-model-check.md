---
name: contact-model-check
description: Use when a simulated or real part slips, sticks or jitters on a surface, or when choosing friction and contact parameters in a simulator. Checks the friction cone against the needed tangential force.
---

# Contact model check

1. Resolve the load into a normal part `fn` and a tangential part `ft` in the contact frame. Compute the needed ratio `|ft| / fn`.
2. Compare it with `mu`. Above `mu` the contact slips, whatever the controller does. Say by how much, as a margin `mu - |ft| / fn`.
3. For a tilted plane, the ratio is `tan(theta)`. For several contacts, check each one with its own normal and its own `mu`.
4. In a penalty simulator, check that normal stiffness is high enough that penetration stays small compared with the part, and that the friction cap uses the current normal force.
5. If the real behaviour differs from the margin, suspect `mu` first, then contact geometry, then stiffness.

Return the margin per contact and which contacts slip. Never change parameters.
