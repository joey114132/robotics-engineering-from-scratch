---
name: latency-budget-check
description: Use when a control loop is stable on the bench but oscillates on the real controller, when adding a filter, bus hop or slower loop rate, or before raising kd. Sums the loop delays and returns the delay margin and the largest safe kd.
---

# Latency budget check

1. List every stage from sensor to drive with its delay: sensor read, velocity filter (`n*dt/2` for an n-sample window), bus, compute, drive latch. Add half a period for the held command. Mark each value measured or assumed.
2. For a PD loop on an inertia `J`: crossover `wc` from `J^2 wc^4 = kd^2 wc^2 + kp^2`, phase margin `atan(kd*wc/kp)`, delay margin `PM / wc`.
3. Compare the total delay with the delay margin. Below about 0.5 of the margin is comfortable, above 1.0 the loop is unstable. Past the optimum a larger `kd` lowers the margin.
4. Report the largest `kd` whose delay margin covers the total delay. A real loop also has a plant that is not a pure inertia, so treat this as an upper bound and confirm in simulation.

Return the budget table, the margin and the `kd` limit. Never change gains on a real drive.
