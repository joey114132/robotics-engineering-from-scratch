---
name: behaviour-tree-review
description: Use when writing or reviewing robot task logic as a behaviour tree or state machine, when a task repeats finished steps after a failure, or when a retry or recovery is bolted on with flags. Checks resume, retry, fallback and tick cost.
---

# Behaviour tree review

1. Write the tree as a list of nodes with the answer each can return (success, failure, running). Flag any leaf that blocks instead of returning running.
2. For every Sequence and Fallback, state whether it keeps a running child across ticks. Test that a finished sibling is not ticked again after a running child resumes.
3. For every Retry, test three cases: success on the last try, failure after the last try, and running between tries.
4. Check that each Fallback ends in a safe action for the robot, and that a root failure is reported, not hidden.
5. Compare with a state-machine table only if the task has few states and no recovery paths.

Return a tick log for one failing run and the list of nodes that were re-ticked after finishing. Never mark a tree correct from reading it; run it on scripted leaves.
