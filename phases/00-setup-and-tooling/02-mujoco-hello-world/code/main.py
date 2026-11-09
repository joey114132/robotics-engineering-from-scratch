# 레슨 00/02: semi-implicit Euler 진자 시뮬레이터와 같은 진자의 MuJoCo 주기 측정
import numpy as np

G = 9.81
MJCF = """<mujoco><option timestep="{dt}" gravity="0 0 -9.81"/><worldbody><body>
<joint name="hinge" type="hinge" axis="0 1 0" damping="0"/>
<inertial pos="0 0 -{L}" mass="1" diaginertia="1e-6 1e-6 1e-6"/></body></worldbody></mujoco>"""


def step(theta, omega, dt, L=1.0, scheme="semi"):
    """One physics step of a point-mass pendulum. semi: update velocity first, then position with the NEW velocity."""
    omega_new = omega - dt * (G / L) * np.sin(theta)
    return theta + dt * (omega_new if scheme == "semi" else omega), omega_new


def simulate(theta0, dt, seconds, L=1.0, scheme="semi") -> np.ndarray:
    theta, omega, out = theta0, 0.0, [theta0]
    for _ in range(int(round(seconds / dt))):
        theta, omega = step(theta, omega, dt, L, scheme)
        out.append(theta)
    return np.array(out)


def energy(theta, dt, L=1.0) -> np.ndarray:
    """Energy per unit mass, with velocity estimated from neighbouring samples."""
    omega = np.gradient(theta, dt)
    return 0.5 * (L * omega) ** 2 + G * L * (1 - np.cos(theta))


def measure_period(theta, dt) -> float:
    """Mean time between upward zero crossings, with linear interpolation inside the step."""
    i = np.where((theta[:-1] < 0) & (theta[1:] >= 0))[0]
    t = (i + -theta[i] / (theta[i + 1] - theta[i])) * dt
    return float(np.mean(np.diff(t)))


def mujoco_period(theta0, dt, seconds, L=1.0) -> float:
    import mujoco  # Use It: the same pendulum, with MuJoCo doing the physics step

    model = mujoco.MjModel.from_xml_string(MJCF.format(dt=dt, L=L))
    data = mujoco.MjData(model)
    data.qpos[0] = theta0
    traj = [theta0]
    for _ in range(int(round(seconds / dt))):
        mujoco.mj_step(model, data)
        traj.append(float(data.qpos[0]))
    return measure_period(np.array(traj), dt)


if __name__ == "__main__":
    print("formula  :", 2 * np.pi * np.sqrt(1.0 / G))
    print("numpy    :", measure_period(simulate(0.05, 0.001, 20.0), 0.001))
    print("mujoco   :", mujoco_period(0.05, 0.001, 20.0))
