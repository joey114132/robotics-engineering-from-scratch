# Behaviour Trees and State Machines

> A robot task is a tree that is ticked every cycle, and every node answers success, failure or running.

**Type:** Build   **Prerequisites:** 05/02 Executors and Callbacks   **Time:** ~15 minutes

## In Plain Words

You put on a shoe, then tie its laces. If a knot slips, you retry the knot without taking the shoe off and
starting again. Remembering the unfinished step keeps a small failure from restarting the whole job.

A behaviour tree does that with success, failure and running answers. This lesson's Sequence remembers a
running child. Retry gives a failed action another attempt, while Fallback tries an alternative. A state
machine records the same decisions as explicit transitions between named states.

## The Problem

You write a fetch task as nested ifs inside one callback. The grasp fails, the callback runs again next cycle, and it no longer knows whether the robot already reached the object. So it drives there again, or it skips the retry. Task logic needs a place to keep "where was I" that is not a pile of flags.

## The Concept

![A fetch task as a tree](../assets/diagram-fetch-tree.png)

*The task is a Sequence of steps. The grasp sits under a Retry, so a failed grasp does not end the whole task.*

Every cycle the root is ticked, and the tick walks down. A leaf does a little work and returns `success`, `failure` or `running`. A parent reads those answers and decides what to do next.

![What a parent does with each answer](../assets/diagram-status-rules.png)

*Sequence stops at the first failure and Fallback stops at the first success. Both remember the child that said running and resume there.*

![Which nodes tick on which cycle](../assets/fig-fetch-ticks.png)

*The grasp fails twice and the Retry reports running. Once go object succeeds, it is never ticked again.*

A state machine is the other common tool. It is a table of `state -> event -> next state`. Every state lists its own exits, so adding a retry means editing every state that can fail. In a tree the retry is one node around one child.

## Build It

```python
def tick(self, log):
    for k in range(self.i, len(self.children)):
        s = self.children[k].tick(log)
        if s == RUNNING or s == self.stop:
            self.i = k if s == RUNNING else 0
            return self.done(log, s)
```

`Sequence` and `Fallback` share this walk. They differ only in which answer stops it. `Retry` turns a failure into `running` until it has tried `n` times. `fetch_task()` builds the tree above and `run()` ticks it to the end.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/05-behaviour-trees-and-state-machines -q
python3 phases/05-robot-software/05-behaviour-trees-and-state-machines/code/main.py
```

## Use It

BehaviorTree.CPP and `py_trees` use the same core answers and add parallel nodes and a blackboard for shared data. Check that your tree gives the same tick log on the same scripted leaves.

## Ship It

`outputs/skill-behaviour-tree-review.md` reviews a task tree for resume, retry and fallback mistakes.

## Exercises

1. Add a Fallback that sends the robot to a safe pose when the Retry gives up.
2. Make a Sequence without memory that rechecks a condition leaf every tick.
3. Write the fetch task as a state machine table and count the transitions.
