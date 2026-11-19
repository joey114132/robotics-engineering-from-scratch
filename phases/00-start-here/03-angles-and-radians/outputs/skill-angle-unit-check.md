---
name: angle-unit-check
description: Use when a program reads, stores or passes an angle (joint position, heading, rotation) or calls sin, cos or atan2. Checks that the unit is radians in code and that angles are compared by their wrapped difference.
---

# Angle unit check

1. For every angle in the code, write down its unit next to its name (`angle_rad`, `angle_deg`). Sensors and screens often use degrees, and `math` and numpy use radians.
2. Convert at the edge where data comes in or goes out (`deg_to_rad`, `rad_to_deg`). Inside the code keep radians only.
3. Test the unit with a quarter turn: 90 degrees must be about 1.57 radians, and `cos` of it must be about 0.
4. To compare two directions, wrap their difference, not each angle: `(a - b + pi) % (2 * pi) - pi` is the short way round, so 359 and 1 degrees differ by -2. Keep the unwrapped angle of a joint whenever turn counts or limits matter.
5. A large radian value can mean several turns, so confirm the unit from the interface, not from the size.

Report each angle's unit and the quarter-turn test result. Do not guess the unit from the size of the number alone.
