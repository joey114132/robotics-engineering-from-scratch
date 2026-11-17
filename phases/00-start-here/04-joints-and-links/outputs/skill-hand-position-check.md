---
name: hand-position-check
description: Use when you compute where an arm's hand is from joint angles and link lengths, to check units, the angle reference and a few easy poses before trusting the numbers.
---

# Hand position check

1. Confirm every angle is in radians. A value like 90 or 180 is probably degrees.
2. Confirm what each angle is counted from. The first is counted from straight across, each later one from the link before it.
3. Test three easy poses by hand: all angles zero (links stretched across), the first angle a quarter turn (links straight up), and the elbow folded fully back (hand close to the shoulder).
4. Check the hand never ends farther than the two link lengths added together.

Report each failed pose with the expected and the actual numbers. Do not change code.
