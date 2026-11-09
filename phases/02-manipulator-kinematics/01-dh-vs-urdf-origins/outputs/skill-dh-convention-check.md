---
name: dh-convention-check
description: Use when a DH table comes from a book, datasheet or another codebase and is about to be used in FK, or when converting between a DH table and URDF-style joint origins. Finds a convention mismatch that raises no error.
---

# DH convention check

1. Ask which convention the table uses. Craig puts `a(i-1), alpha(i-1)` on row `i`; the distal convention puts `a(i), alpha(i)` there. If the source does not say, treat it as unknown.
2. Check the routine's step order (`Rx Tx Rz Tz` for Craig, `Rz Tz Tx Rx` for standard) against that convention.
3. Evaluate FK at 5 or more random poses and compare with a second description (URDF origins, a CAD measurement, or a closed form). Never accept a check made only at the zero pose.
4. When converting, shift `(a, alpha)` by one row for DH to DH, and refuse any conversion that would drop a theta offset.

Return the convention found, the tip error at each test pose, and the first row where the two descriptions differ. Never edit the table silently.
