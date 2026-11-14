# Traffic and Deadlock

> At a single-lane crossing robots can block each other in a loop. Draw who waits for whom, find the loop, and remove it by taking a whole route at once.

**Type:** Build   **Prerequisites:** a graph as nodes and arrows   **Time:** ~15 minutes

## In Plain Words

Four toy cars meet at a crossing. Each stops on a square the next car needs and waits for the square ahead. The waits form a loop, so politely waiting leaves every car stuck forever.

The traffic model calls this deadlock. If a car enters only when its whole route is clear and then reserves it, a car waiting outside holds no square another car needs. The loop cannot form, but reserved routes keep other cars from passing.

## The Problem

Four robots enter a small junction, each stopping on one intersection because the next is taken. Each holds what the next needs, so none can move and throughput, the jobs finished per tick, drops to zero. Nothing is broken: every robot politely waited for a free cell.

## The Concept

![Wait-for loop](../assets/diagram-wait-cycle.png)

*An arrow means "waits for the car standing there". A loop is a deadlock: no car in it can ever move.*

![Reservation](../assets/diagram-reservation.png)

*A robot enters only if its whole route is free, then holds it. A robot that waits outside holds nothing, so no one waits on it.*

![Throughput](../assets/fig-throughput.png)

*Left: 8 robots, 40 jobs, mean of 30 layouts: "move if free" freezes near 3.5 jobs finished while reservation finishes all 40. Right: jobs finished by tick 30 against robots on the grid. The naive rule deadlocks more as robots are added, and reservation levels off near 31 because whole routes block each other, its price.*

The deadlock needs four conditions at once: one robot per cell, hold-and-wait (a robot holds a cell while waiting for the next), no pushing (nobody is forced out) and circular wait (the waits form a loop). Reservation removes hold-and-wait.

In the clip, four cars start on a 2 x 2 grid of cells, each needing the next car's cell: car 0 drives (0,0), (1,0), (1,1), car 1 (1,0), (1,1), car 2 (1,1), (0,1), car 3 (0,1), (0,0). With `naive` all four enter at tick 1 and `find_cycle()` returns the cars on the loop, `[0, 1, 2, 3]`. With `reserve` car 0 takes its three cells first, the others wait outside, and all four finish by tick 7.

![Reserved cells and stop bars](../assets/clip-example.mp4)

*`reserve` at 0.7 s per tick. A red bar stops a waiting car even when the cell ahead looks free, because its whole route is not free. Amber marks reserved cells.*

## Build It

`Sim.wait_for()` returns for each robot the robot standing on its next cell. `find_cycle()` follows those pointers. The `reserve` policy admits a robot only if every node on its route is free.

```python
need = p if self.policy == "reserve" else p[:1]
if len(self.at) < self.K and all(n not in self.occ and n not in self.res for n in need):
```

Tests check the four-robot loop is found and that under reservation the wait-for graph is empty at every tick on 40 random jobs.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/14-multi-robot-and-swarms/03-traffic-and-deadlock -q
python3 phases/14-multi-robot-and-swarms/03-traffic-and-deadlock/code/figure.py
```

## Use It

No external source was used. Cross-check `find_cycle` against a graph library's cycle finder, and try time-window reservations to win back the throughput lost to whole-route holding.

## Ship It

`outputs/skill-traffic-deadlock.md` is a review checklist for a fleet traffic rule.

## Exercises

1. Replace the reservation with "back up one cell when a loop is detected" and compare throughput.
2. Let robots take cells one at a time but only in a fixed global cell order, and check the loop cannot form.
3. Add a 6 x 6 grid and find the robot count where reservation stops improving.
