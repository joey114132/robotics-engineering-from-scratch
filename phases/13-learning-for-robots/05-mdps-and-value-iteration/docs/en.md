# MDPs and Value Iteration

> The value of a state is the best action's reward plus the discounted value of where it leads, and repeated sweeps find it.

**Type:** Build   **Prerequisites:** 09/05 Grid Search: Dijkstra to A*   **Time:** ~15 minutes

## In Plain Words

A rover drives on a slippery floor: one move in five slides sideways. A shortcut beside a pit can be worse than a longer route, because one slide drops the rover in.

An MDP (Markov decision process) lists each move's outcomes and chances. Value iteration scores a move by its reward now plus the later value of where it may lead, averaged by chance. One pass over every tile is a sweep. Sweeps repeat, spreading the goal's good and the pit's bad news, until every tile has a best move.

## The Problem

In 13/03 a policy found its way from sampled returns, and you could only hope it was near the best. On a small problem you can know: compute the best answer exactly, and every learned policy has a yardstick.

## The Concept

![One backup of one state](../assets/diagram-bellman-backup.png)

*Follow the numbers. A backup recomputes one tile's value: score each action by its reward now plus gamma times the value of its outcomes, and keep the best score.*

An MDP is states (tiles), actions (moves), a transition chance `P(s' | s, a)` (chance of reaching tile s' from s by move a) and a reward. The value `V(s)` is the reward-to-go from 13/03, averaged over chance, assuming the best actions from here on. The discount gamma (0.9 here) shrinks a reward one step later by that factor, since sooner is better.

![The sweep loop](../assets/diagram-value-iteration-loop.png)

*Start at zero, back up every state, repeat. Settled values give the greedy policy: the best-scoring action in each cell.*

![Value spreading from the goal](../assets/fig-value-ripple.png)

*Top: value reaches farther from the goal with every sweep, and the pit repels paths. Bottom: the gap to the final values shrinks at least as fast as gamma to the k (k = sweep number).*

The tile just right of the pit. After the first sweep, when every value is still 0, moving left scores -0.8 (chance 0.8 of the pit's -1) and moving right 0. After 29 sweeps (`value_iteration()`) right scores 0.64, up or down 0.43, left -0.68. The tile's value is 0.64 and its arrow points right.

![Rover with four score arrows](../assets/clip-example.mp4)

*Watch the arrows: each move's score, blue above zero, red below. The best turns green and the rover takes it.*

## Build It

Moves slip sideways with chance 0.2; the goal pays 1 and the pit -1.

```python
def backup(model, V, gamma):
    return model.r + gamma * model.P @ V      # Q[a, s]

V = backup(model, V, gamma).max(0)            # one sweep
pi = backup(model, V, gamma).argmax(0)        # greedy policy
```

Tests check contraction, the sweep bound and all 256 policies of a tiny grid. For `0 < gamma < 1` and `delta1 = max(abs(V1 - V0))`, the kth change is at most `gamma**(k - 1) * delta1`; the bound is the first k that pushes this strictly below `tol`.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/05-mdps-and-value-iteration -q
python3 phases/13-learning-for-robots/05-mdps-and-value-iteration/code/figure.py
```

## Use It

The loop needs the whole model, so it cannot run when the dynamics are unknown; policy gradients exist for that case.

Sources: Sutton and Barto, *Reinforcement Learning: An Introduction*, 2nd ed. draft, section 4.4, opened 2026-11-10. It describes value iteration as one-sweep policy evaluation combined with improvement.

## Ship It

`outputs/skill-value-iteration-oracle.md` turns a small simulated task into an exact reference policy.

## Exercises

1. Raise `slip` from 0.2 to 0.5 and find where the policy first avoids the pit.
2. Set `gamma` to 0.5 and compare the sweep count with the bound.
3. Run 13/03's policy gradient here and compare its return with `V` at the start cell.
