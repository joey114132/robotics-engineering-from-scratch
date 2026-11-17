# Behaviour Trees and State Machines

> Learn how a robot task can remember where it is, so a failed step is retried instead of restarted.

**Type:** Build   **Prerequisites:** 05/02 Executors and Callbacks   **Time:** ~15 minutes

## In Plain Words

An arm fetches a crate. If the grasp misses, it should retry where it is, not drive back to the start. A behaviour tree gives it that memory.

## Key Terms

- **Behaviour tree**: a task written as a tree of steps and ticked every cycle.
- **Tick**: one small step, where the tree is asked to do a little work and report.
- **Status**: the answer a node gives, `success`, `failure` or `running`.
- **Sequence**: a parent that runs its children in order and stops at the first failure.
- **Fallback**: a parent that tries its children in order and stops at the first success.
- **State machine**: a table of named states with an arrow for each event.

## The Problem

An arm reaches a crate, grasps it and carries it. As nested ifs, a missed grasp makes the code forget whether the arm already reached the crate, so it drives there again.

## The Concept

Real tasks fail halfway all the time, so the task needs a place to remember where it was.

![A fetch task as a tree](../assets/diagram-fetch-tree.png)

*The grasp sits under a Retry, so a miss does not end the task.*

Every cycle the tree is ticked and each step answers success, failure or running. A Sequence stops at the first failure, a Fallback at the first success, and both resume at the step that said running.

![What a parent does with each answer](../assets/diagram-status-rules.png)

*What a parent does with each answer.*

A Fallback tries bin A, then bin B. Bin A is full, so it moves on to bin B, which answers running. The next tick resumes at bin B without asking about A again.

![An arm skips a full bin](../assets/clip-example.mp4)

*A red frame flashes on the full bin. The arm then carries the crate to bin B.*

![Which nodes tick on which cycle](../assets/fig-fetch-ticks.png)

*The grasp fails twice and the Retry reports running. Reach, once done, is not ticked again.*

A state machine needs a retry added to every state that can fail. A tree needs one node around one child.

<details><summary>The math (optional)</summary>

In the bin example, tick 1 fails the check `A has room` and moves on to `go B`, which answers running. Tick 2 resumes at `go B`, and tick 3 succeeds. `Retry` turns a failure into `running` until it has tried `n` times.

</details>

## Build It

```python
def tick(self, log):
    for k in range(self.i, len(self.children)):
        s = self.children[k].tick(log)
        if s == RUNNING or s == self.stop:
            self.i = k if s == RUNNING else 0
            return self.done(log, s)
```

`Sequence` and `Fallback` share this walk and differ only in which answer stops it.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/05-behaviour-trees-and-state-machines -q
python3 phases/05-robot-software/05-behaviour-trees-and-state-machines/code/main.py
```

## Use It

BehaviorTree.CPP and `py_trees` use the same answers and add shared data.

## Ship It

`outputs/skill-behaviour-tree-review.md` reviews a task tree for resume, retry and fallback mistakes.

## Exercises

1. Add a Fallback that moves the robot to a safe pose when the Retry gives up.
2. Make a Sequence recheck a condition every tick.
3. Write the fetch task as a state machine table.
