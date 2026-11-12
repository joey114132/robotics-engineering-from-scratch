# 레슨 13/05: 미끄러지는 격자 MDP 의 value iteration, 수렴 기록, 탐욕 정책 추출
from collections import namedtuple

import numpy as np

MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right as (row, col) steps
SIDEWAYS = {0: (2, 3), 1: (2, 3), 2: (0, 1), 3: (0, 1)}  # the two actions a slip can turn each action into
REWARD = {"G": 1.0, "X": -1.0}  # reward for entering a goal or a pit cell; both end the episode
Model = namedtuple("Model", "P r n term idx cells")


def gridworld(layout, slip=0.0):
    """Layout chars: '.' free, '#' wall, 'G' goal, 'X' pit. P[a, s, s'] and expected reward r[a, s]."""
    cells = [(i, j) for i, row in enumerate(layout) for j, c in enumerate(row) if c != "#"]
    idx = {c: s for s, c in enumerate(cells)}
    n = len(cells)
    P, r, term = np.zeros((4, n, n)), np.zeros((4, n)), np.zeros(n, bool)
    for (i, j), s in idx.items():
        if layout[i][j] in REWARD:
            term[s], P[:, s, s] = True, 1.0  # absorbing, worth 0 after the entry reward was paid
            continue
        for a in range(4):
            for b, p in ((a, 1 - slip), (SIDEWAYS[a][0], slip / 2), (SIDEWAYS[a][1], slip / 2)):
                t = idx.get((i + MOVES[b][0], j + MOVES[b][1]), s)  # a wall or the edge keeps the robot in place
                P[a, s, t] += p
                r[a, s] += p * REWARD.get(layout[cells[t][0]][cells[t][1]], 0.0)
    return Model(P, r, n, term, idx, cells)


def backup(model, V, gamma):
    """Q[a, s] = expected reward now + gamma * expected value of where the action leads."""
    return model.r + gamma * model.P @ V


def value_iteration(model, gamma, tol=1e-6):
    """Sweep every state with the best action's backup until V stops moving. Returns V, every V so far, sweeps."""
    V = np.zeros(model.n)
    hist = [V]
    while True:
        V_new = backup(model, V, gamma).max(0)
        hist.append(V_new)
        done = np.abs(V_new - V).max() < tol
        V = V_new
        if done:
            return V, hist, len(hist) - 1


def greedy(model, V, gamma):
    return backup(model, V, gamma).argmax(0)


def evaluate(model, pi, gamma):
    """Exact value of a fixed policy: solve (I - gamma * P_pi) V = r_pi."""
    s = np.arange(model.n)
    return np.linalg.solve(np.eye(model.n) - gamma * model.P[pi, s], model.r[pi, s])


if __name__ == "__main__":
    model = gridworld(["......G", ".##.##.", "...X...", ".#.##..", "......."], slip=0.2)
    V, hist, sweeps = value_iteration(model, 0.9)
    print("sweeps", sweeps, "bound", 1 + int(np.ceil(np.log(1e-6) / np.log(0.9))))
    print("start value", round(V[model.idx[(4, 0)]], 3), "arrow", "^v<>"[greedy(model, V, 0.9)[model.idx[(4, 0)]]])
