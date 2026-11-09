# 레슨 03/05 테스트: 2링크 M, Coriolis 를 운동에너지·수치 Lagrangian 으로 검증하고 computed torque 대 PD 추종 오차를 비교한다
import importlib.util
import pathlib

import numpy as np

_p = pathlib.Path(__file__).resolve().parents[1] / "main.py"
_spec = importlib.util.spec_from_file_location("lesson_ct", _p)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)

P = m.PARAMS
RNG = np.random.default_rng(3)


def kinetic(q, qd):
    """Kinetic energy from Cartesian centre-of-mass velocities, independent of the formula in main.py."""
    s1, c1, s12, c12 = np.sin(q[0]), np.cos(q[0]), np.sin(q[0] + q[1]), np.cos(q[0] + q[1])
    w2 = qd[0] + qd[1]
    v1 = P["lc1"] * qd[0] * np.array([-s1, c1])
    v2 = P["l1"] * qd[0] * np.array([-s1, c1]) + P["lc2"] * w2 * np.array([-s12, c12])
    return 0.5 * P["m1"] * v1 @ v1 + 0.5 * P["I1"] * qd[0] ** 2 + 0.5 * P["m2"] * v2 @ v2 + 0.5 * P["I2"] * w2**2


def test_mass_matrix_is_symmetric_positive_definite_everywhere():
    for _ in range(50):
        M = m.mass(RNG.uniform(-3, 3, 2), P)
        assert np.allclose(M, M.T) and np.all(np.linalg.eigvalsh(M) > 0)


def test_mass_matrix_reproduces_cartesian_kinetic_energy():
    for _ in range(20):
        q, qd = RNG.uniform(-3, 3, 2), RNG.uniform(-2, 2, 2)
        assert np.isclose(0.5 * qd @ m.mass(q, P) @ qd, kinetic(q, qd))


def test_inverse_dynamics_matches_numeric_lagrangian():
    eps = 1e-5
    for _ in range(10):
        q, qd, qdd = RNG.uniform(-2, 2, 2), RNG.uniform(-2, 2, 2), RNG.uniform(-3, 3, 2)

        def mom(t):  # dT/dqd at time t along q(t) = q + qd t + qdd t^2 / 2
            qt, vt = q + qd * t + 0.5 * qdd * t**2, qd + qdd * t
            return np.array([(kinetic(qt, vt + eps * e) - kinetic(qt, vt - eps * e)) / (2 * eps) for e in np.eye(2)])

        dmom = (mom(eps) - mom(-eps)) / (2 * eps)
        dTdq = np.array([(kinetic(q + eps * e, qd) - kinetic(q - eps * e, qd)) / (2 * eps) for e in np.eye(2)])
        assert np.allclose(dmom - dTdq, m.inverse_dynamics(q, qd, qdd, P), atol=2e-4)


def test_free_motion_conserves_kinetic_energy():
    q, qd = np.array([0.3, 0.8]), np.array([2.0, -1.0])
    e0 = kinetic(q, qd)
    for _ in range(1000):
        q, qd = m.rk4_step(q, qd, np.zeros(2), 1e-3, P)
    assert np.isclose(kinetic(q, qd), e0, rtol=1e-7)


def test_forward_dynamics_inverts_inverse_dynamics():
    q, qd, qdd = np.array([0.4, -0.9]), np.array([1.0, 2.0]), np.array([5.0, -7.0])
    assert np.allclose(m.forward_dynamics(q, qd, m.inverse_dynamics(q, qd, qdd, P), P), qdd)


def test_computed_torque_tracks_a_fast_trajectory_far_better_than_pd():
    e_ct = m.tracking_error(m.computed_torque, P, P)
    e_pd = m.tracking_error(m.pd_control, P, P)
    assert e_ct.max() < 2e-3 and e_pd.max() > 0.1  # CT floor is the 1 ms hold of the reference acceleration
    assert e_pd.max() > 100 * e_ct.max()


def test_error_decays_like_critically_damped_second_order_system():
    w, e0 = m.OMEGA, 0.1
    e = m.tracking_error(m.computed_torque, P, P, q0_offset=np.array([e0, 0.0]), norm=False)[:, 0]
    t = 0.2
    assert np.isclose(e[int(t / m.DT)], -e0 * (1 + w * t) * np.exp(-w * t), rtol=0.05)  # e = ref - q, q starts ahead


def test_computed_torque_with_wrong_masses_still_beats_pd():
    wrong = dict(P, m1=1.2 * P["m1"], m2=0.8 * P["m2"])
    assert m.tracking_error(m.computed_torque, P, wrong).max() < m.tracking_error(m.pd_control, P, wrong).max() / 3


def test_inverse_dynamics_matches_mujoco_mj_inverse():
    mujoco = __import__("pytest").importorskip("mujoco")
    xml = """<mujoco><option gravity="0 0 0"/><worldbody>
    <body><joint type="hinge" axis="0 0 1"/><inertial pos="0.25 0 0" mass="1" diaginertia="0.02 0.02 0.02"/>
    <body pos="0.5 0 0"><joint type="hinge" axis="0 0 1"/><inertial pos="0.25 0 0" mass="1" diaginertia="0.02 0.02 0.02"/>
    </body></body></worldbody></mujoco>"""  # same arm as PARAMS: m=1, l1=0.5, lc=0.25, I=0.02
    model = mujoco.MjModel.from_xml_string(xml)
    data = mujoco.MjData(model)
    for _ in range(5):
        q, qd, qdd = RNG.uniform(-2, 2, 2), RNG.uniform(-2, 2, 2), RNG.uniform(-3, 3, 2)
        data.qpos[:], data.qvel[:], data.qacc[:] = q, qd, qdd
        mujoco.mj_inverse(model, data)
        assert np.allclose(data.qfrc_inverse, m.inverse_dynamics(q, qd, qdd, P), atol=1e-9)
