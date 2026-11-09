# 레슨 16/03: 시연 데이터로 만든 nearest-neighbour 도달 정책과, 정책 바깥에서 clip, 변화율 제한, stale hold 를 하는 결정적 안전 wrapper
import numpy as np

DT, J, B, UMAX = 0.02, 1.0, 0.5, 3.0  # step (s), inertia, viscous drag, torque limit (Nm)


def plant(q, v, u):
    """One damped joint, semi-implicit Euler: J dv/dt = u - B v."""
    v = v + DT * (u - B * v) / J
    return q + DT * v, v


def expert(obs):
    """PD toward the target with a saturated torque. obs = (error, velocity)."""
    return float(np.clip(8.0 * obs[0] - 4.0 * obs[1], -UMAX, UMAX))


def demos(n_episodes=40, steps=100, seed=0):
    """Expert reaching episodes from random starts to random targets, as (observation, action) pairs."""
    rng, X, Y = np.random.default_rng(seed), [], []
    for _ in range(n_episodes):
        q, v, target = rng.uniform(-1.5, 1.5), 0.0, rng.uniform(-1.0, 1.0)
        for _ in range(steps):
            obs = np.array([target - q, v])
            X.append(obs), Y.append(expert(obs))
            q, v = plant(q, v, Y[-1])
    return np.array(X), np.array(Y)


def fit(X, Y, k=5):
    """Behaviour cloning by nearest neighbours: the action is the mean of the k closest demonstrations."""
    def policy(obs):
        d = ((X - obs) ** 2).sum(1)
        return float(Y[np.argpartition(d, k)[:k]].mean())
    return policy


class Safety:
    """Deterministic wrapper: hold on a stale observation, clip to the torque limit, limit the change per step."""

    def __init__(self, umax=UMAX, du=0.5, max_age=3):
        self.umax, self.du, self.max_age, self.u = umax, du, max_age, 0.0
        self.n = dict(clip=0, rate=0, hold=0)  # intervention counts

    def __call__(self, raw, age):
        if age > self.max_age:  # the observation is too old to act on: command zero torque
            raw, self.n["hold"] = 0.0, self.n["hold"] + 1
        c = float(np.clip(raw, -self.umax, self.umax))
        r = self.u + float(np.clip(c - self.u, -self.du, self.du))
        self.n["clip"] += c != raw
        self.n["rate"] += r != c
        self.u = r
        return r


def rollout(policy, target, steps=150, q0=0.0, safety=None, glitch=None, drop=()):
    """Run the policy on the joint. glitch maps step -> value added to the action; drop lists steps whose observation is lost."""
    q, v, age, last = q0, 0.0, 0, np.array([target - q0, 0.0])
    Q, U = [], []
    for k in range(steps):
        age = age + 1 if k in drop else 0
        if age == 0:
            last = np.array([target - q, v])  # a lost observation leaves the last one in place
        a = policy(last) + (glitch or {}).get(k, 0.0)
        u = safety(a, age) if safety else a
        q, v = plant(q, v, u)
        Q.append(q), U.append(u)
    return dict(q=np.array(Q), u=np.array(U), n=safety.n if safety else {})


if __name__ == "__main__":
    X, Y = demos()
    pi = fit(X, Y)
    for name, kw in (("clean", {}), ("spike at step 30", dict(glitch={30: 40.0})), ("observation lost 10..35", dict(drop=range(10, 36)))):
        for label, s in (("raw", None), ("wrapped", Safety())):
            r = rollout(pi, 1.0, safety=s, **kw)
            print(f"{name:24s} {label:8s} peak |u| {np.abs(r['u']).max():5.1f}  peak q {r['q'].max():.2f}  final q {r['q'][-1]:.3f}  interventions {r['n']}")
