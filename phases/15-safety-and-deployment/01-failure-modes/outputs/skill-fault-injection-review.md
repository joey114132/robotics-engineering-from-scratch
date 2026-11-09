---
name: fault-injection-review
description: Use when reviewing or designing the safety monitors of a joint or actuator control loop, or before trusting that a loop "would notice" a bad sensor or a bad command. Lists the five faults to inject and what to ask about each monitor.
---

# Fault-injection review

1. In simulation, inject each fault into the loop: stuck sensor, sensor dropout, delayed feedback, actuator saturation, wrong sign. Apply sign and saturation from the first tick and the sensor faults mid-move.
2. Measure on the true plant, not the controller's view: did the joint reach a limit, when, and where does it end.
3. Measure detectability from the controller's own signals only: frozen reading while torque is applied, one-tick jump, error growing, still not at target after a deadline.
4. Rank by reached-limit, final error, speed. For each fault that reaches a limit, require that the first alarm comes earlier.
5. Name the quiet faults (alarm only by a deadline or never) and say which monitor or test must cover them.

Report a table of fault, peak, final error, time to limit, time to alarm. State that thresholds were measured on this plant only.
