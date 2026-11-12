---
name: euler-angle-audit
description: Use when a system stores, filters, differentiates or logs roll-pitch-yaw, when angles jump by 180 degrees, or when a controller commands huge rates near a vertical tool. Finds where Euler angles are used where a rotation matrix or quaternion belongs.
---

# Euler angle audit

1. List every place an orientation is stored, interpolated, filtered or differentiated as roll, pitch, yaw. Note the axis order for each.
2. Sweep pitch from 0 to 89.9 degrees through each place. Log `det E = cos(pitch)` and the largest Euler rate for a 1 rad/s spin.
3. Cross 90 degrees. If roll or yaw jumps by about 180 degrees, mark the place as using a single spelling.
4. Recommend a rotation matrix or unit quaternion inside, with Euler angles only for display. Name where wrapping and `locked` must be handled.

Return a table of places, axis order, the pitch where it breaks and the fix. Never change the axis order without saying so.
