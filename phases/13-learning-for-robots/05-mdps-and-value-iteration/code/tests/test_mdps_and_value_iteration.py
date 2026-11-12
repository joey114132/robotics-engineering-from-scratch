# 레슨 13/05 테스트: value iteration 의 수렴 횟수 상한, 수축, 손풀이 정책, 전수 비교
import importlib.util
import itertools
import math
import pathlib
import re

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_mdp", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

CLIFF = [".....", "....G", "XXXX."]  # the short way along row 1 runs beside the pits
RIGHT, UP = 3, 0


def test_artifact_sweep_bound_accounts_for_reward_scale_and_strict_stopping():
    artifact = _p.parents[1] / "outputs" / "skill-value-iteration-oracle.md"
    blocks = re.findall(r"```python\n(.*?)```", artifact.read_text(), re.DOTALL)
    namespace = {}
    for block in blocks:
        exec(block, namespace)
    bound_for = namespace["sweep_bound"]
    for reward, gamma, tol in [(10.0, 0.9, 1e-6), (1.0, 0.5, 0.125), (0.0, 0.9, 1e-6)]:
        model = m.Model(np.ones((1, 1, 1)), np.array([[reward]]), 1, np.zeros(1, bool), {}, [])
        _, hist, sweeps = m.value_iteration(model, gamma, tol)
        delta1 = float(np.abs(hist[1] - hist[0]).max())
        bound = bound_for(delta1, gamma, tol)
        assert sweeps <= bound
        assert delta1 * gamma ** (bound - 1) < tol
    assert bound_for(1.0, 0.5, 0.125) == 5  # Equality at sweep 4 does not meet < tol.


def test_corridor_matches_the_hand_solution():
    model = m.gridworld(["..G"], slip=0.0)
    V, _, _ = m.value_iteration(model, gamma=0.9)
    assert np.allclose(V[:2], [0.9, 1.0], atol=1e-6)  # V(next to goal) = 1, V(one further) = 0.9 * 1
    assert list(m.greedy(model, V, 0.9)[:2]) == [RIGHT, RIGHT]


def test_backup_is_a_contraction_with_factor_gamma():
    model, rng, gamma = m.gridworld(CLIFF, slip=0.2), np.random.default_rng(0), 0.9
    for _ in range(50):
        V, W = rng.normal(size=model.n) * 5, rng.normal(size=model.n) * 5
        gap_after = np.abs(m.backup(model, V, gamma).max(0) - m.backup(model, W, gamma).max(0)).max()
        assert gap_after <= gamma * np.abs(V - W).max() + 1e-12


def test_sweeps_stay_under_the_bound_and_error_shrinks_by_gamma_each_sweep():
    gamma, tol = 0.9, 1e-6
    model = m.gridworld(CLIFF, slip=0.2)
    V, hist, sweeps = m.value_iteration(model, gamma, tol)
    assert sweeps <= 1 + math.ceil(math.log(tol) / math.log(gamma))  # first sweep moves V by at most 1 (rewards <= 1)
    star = np.abs(V).max()
    for k, Vk in enumerate(hist):
        assert np.abs(Vk - V).max() <= gamma ** k * star + 1e-5


def test_fixed_point_satisfies_the_bellman_equation():
    model = m.gridworld(CLIFF, slip=0.2)
    V, _, _ = m.value_iteration(model, 0.9)
    assert np.abs(m.backup(model, V, 0.9).max(0) - V).max() < 1e-5


def test_greedy_policy_beats_every_other_policy_on_a_tiny_mdp():
    model, gamma = m.gridworld(["..G", ".X."], slip=0.2), 0.9
    V, _, _ = m.value_iteration(model, gamma)
    live = [s for s in range(model.n) if not model.term[s]]
    for combo in itertools.product(range(4), repeat=len(live)):
        pi = np.zeros(model.n, int)
        pi[live] = combo
        assert (m.evaluate(model, pi, gamma) <= V + 1e-5).all()
    assert np.allclose(m.evaluate(model, m.greedy(model, V, gamma), gamma), V, atol=1e-5)


def test_slip_near_a_pit_turns_the_policy_away_from_the_short_way():
    s = m.gridworld(CLIFF, slip=0.0)
    s_slip = m.gridworld(CLIFF, slip=0.4)
    a0 = m.greedy(s, m.value_iteration(s, 0.9)[0], 0.9)[s.idx[(1, 0)]]
    a1 = m.greedy(s_slip, m.value_iteration(s_slip, 0.9)[0], 0.9)[s_slip.idx[(1, 0)]]
    assert (a0, a1) == (RIGHT, UP)
