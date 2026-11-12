# 레슨 05/05: 매 주기 tick 되는 behaviour tree (Sequence, Fallback, Retry)와 비교용 간단한 상태 기계
SUCCESS, FAILURE, RUNNING = "success", "failure", "running"


class Node:
    def __init__(self, name, children=()):
        self.name, self.children, self.i = name, list(children), 0  # i: child that said RUNNING last tick

    def done(self, log, status):
        return log.append((self.name, status)) or status


class Leaf(Node):
    def __init__(self, name, fn):
        super().__init__(name)
        self.fn, self.calls = fn, 0

    def tick(self, log):
        self.calls += 1
        return self.done(log, self.fn())


class Sequence(Node):
    """Run children in order. First FAILURE ends it, a RUNNING child is resumed next tick."""
    stop, end = FAILURE, SUCCESS

    def tick(self, log):
        for k in range(self.i, len(self.children)):
            s = self.children[k].tick(log)
            if s == RUNNING or s == self.stop:
                self.i = k if s == RUNNING else 0
                return self.done(log, s)
        self.i = 0
        return self.done(log, self.end)


class Fallback(Sequence):
    """Same walk, but the first SUCCESS ends it and it fails only when every child failed."""
    stop, end = SUCCESS, FAILURE


class Retry(Node):
    def __init__(self, name, tries, child):
        super().__init__(name, [child])
        self.tries, self.used = tries, 0

    def tick(self, log):
        s = self.children[0].tick(log)
        if s == FAILURE:
            self.used += 1
            s = RUNNING if self.used < self.tries else FAILURE
        self.used = self.used if s == RUNNING else 0
        return self.done(log, s)


def condition(name, test):
    return Leaf(name, lambda: SUCCESS if test() else FAILURE)


def scripted(name, statuses):
    """A leaf that replays a list of statuses, then repeats the last one."""
    it = iter(statuses)
    return Leaf(name, lambda: next(it, statuses[-1]))


def run(tree, max_ticks=50):
    """Tick until the root is no longer RUNNING. Returns [(log, status)] per tick."""
    out = []
    while len(out) < max_ticks and (not out or out[-1][1] == RUNNING):
        log = []
        out.append((log, tree.tick(log)))
    return out


def fetch_task():
    """Go to the object, grasp (fails twice, retried up to 3 times), go to the bin, release."""
    L = dict(go_object=scripted("go object", [RUNNING, RUNNING, SUCCESS]), grasp=scripted("grasp", [FAILURE, FAILURE, SUCCESS]),
             go_bin=scripted("go bin", [RUNNING, SUCCESS]), release=scripted("release", [SUCCESS]))
    return Sequence("fetch", [L["go_object"], Retry("retry", 3, L["grasp"]), L["go_bin"], L["release"]]), L


def fsm_step(table, state, event):
    """A state machine lists every exit of every state. Unknown events leave the state alone."""
    return table.get(state, {}).get(event, state)


if __name__ == "__main__":
    for n, (log, s) in enumerate(run(fetch_task()[0]), 1):
        print(n, s, [name for name, _ in log])
