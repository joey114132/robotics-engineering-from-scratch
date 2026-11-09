# 레슨 14/03: 격자 위 로봇 교통, 교차로 교착을 wait-for graph 로 찾고 경로 예약으로 푼다
def xy_path(a, b) -> list:
    """Drive along x first, then along y. Nodes are grid intersections that hold one robot at a time."""
    (x, y), (X, Y), p = a, b, [a]
    while x != X:
        x += 1 if X > x else -1
        p.append((x, y))
    while y != Y:
        y += 1 if Y > y else -1
        p.append((x, y))
    return p


def find_cycle(g: dict):
    """g[r] = the one robot r waits for. Returns the robots on a cycle or None (follow the pointers)."""
    for start in g:
        seen, r = [], start
        while r in g and r not in seen:
            seen.append(r)
            r = g[r]
        if r in seen:
            return seen[seen.index(r):]
    return None


class Sim:
    def __init__(self, jobs, K, policy):
        self.paths, self.K, self.policy = [xy_path(*j) for j in jobs], K, policy
        self.queue, self.at, self.occ, self.res, self.done = list(range(len(jobs))), {}, {}, {}, 0

    def wait_for(self) -> dict:
        g = {}
        for r, i in self.at.items():
            p = self.paths[r]
            if i + 1 < len(p) and p[i + 1] in self.occ:
                g[r] = self.occ[p[i + 1]]
        return g

    def step(self):
        for r in list(self.queue):  # admit waiting robots
            p = self.paths[r]
            need = p if self.policy == "reserve" else p[:1]  # reserve: the whole route must be free at once
            if len(self.at) < self.K and all(n not in self.occ and n not in self.res for n in need):
                self.queue.remove(r)
                self.at[r], self.occ[p[0]] = 0, r
                if self.policy == "reserve":
                    self.res.update({n: r for n in p})
        moved, changed = set(), True
        while changed:  # a robot moves once per tick; a freed node can let the robot behind it move
            changed = False
            for r in list(self.at):
                p, i = self.paths[r], self.at[r]
                if r in moved:
                    continue
                if i == len(p) - 1:  # at the goal: leave the grid
                    del self.occ[p[i]], self.at[r]
                    self.res.pop(p[i], None)
                    self.done += 1
                elif p[i + 1] not in self.occ:
                    del self.occ[p[i]]
                    self.res.pop(p[i], None)
                    self.occ[p[i + 1]], self.at[r] = r, i + 1
                else:
                    continue
                moved.add(r)
                changed = True


def run(jobs, K, policy, T) -> list:
    s, hist = Sim(jobs, K, policy), []
    for _ in range(T):
        s.step()
        hist.append(s.done)
    return hist


if __name__ == "__main__":
    ring = [((0, 0), (1, 1)), ((1, 0), (1, 1)), ((1, 1), (0, 1)), ((0, 1), (0, 0))]
    s = Sim(ring, 4, "naive"); s.step(); print("cycle:", find_cycle(s.wait_for()))
