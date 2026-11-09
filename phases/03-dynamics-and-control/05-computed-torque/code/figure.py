# 레슨 03/05 그림: PD 대 computed torque 추종 오차와, 관성·Coriolis 항이 궤적을 따라 얼마나 변하는지를 PNG 로 만든다
import importlib.util
import pathlib

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("ct_main", HERE / "main.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)
BLUE, ORANGE, GREY = "#0072B2", "#D55E00", "#555555"
ASSETS = HERE.parent / "assets"
P = m.PARAMS


def save(fig, name):
    fig.tight_layout()
    ASSETS.mkdir(exist_ok=True)
    fig.savefig(ASSETS / name, dpi=100)
    plt.close(fig)
    print(ASSETS / name)


def tracking():
    t = np.arange(2000) * m.DT
    wrong = dict(P, m1=1.2 * P["m1"], m2=0.8 * P["m2"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.4))
    a1.semilogy(t, m.tracking_error(m.pd_control, P, P), color=ORANGE, lw=2, label="joint PD")
    a1.semilogy(t, m.tracking_error(m.computed_torque, P, wrong), color=GREY, lw=2, label="computed torque, masses off by 20%")
    a1.semilogy(t, m.tracking_error(m.computed_torque, P, P), color=BLUE, lw=2, label="computed torque, exact model")
    a1.set_xlabel("time (s)")
    a1.set_ylabel("tracking error norm (rad, log scale)")
    a1.set_title("Exact computed torque: about 300x less error", fontsize=13)
    a1.set_ylim(1e-5, 1.0)
    a1.legend(loc="lower right", fontsize=9)
    a1.grid(alpha=0.3, which="both")
    q, qd = m.trajectory(0.0)[0], np.zeros(2)
    qs = []
    for i in range(2000):
        qs.append(q[0])
        q, qd = m.rk4_step(q, qd, m.pd_control(q, qd, m.trajectory(i * m.DT), P), m.DT, P)
    a2.plot(t, m.trajectory(t[:, None])[0][:, 0], color=GREY, ls="--", lw=2, label="reference")
    a2.plot(t, qs, color=ORANGE, lw=2, label="joint PD")
    a2.set_xlabel("time (s)")
    a2.set_ylabel("joint 1 angle (rad)")
    a2.set_title("PD lags the reference on a 1 s swing", fontsize=13)
    a2.legend(loc="upper right", fontsize=9)
    a2.grid(alpha=0.3)
    save(fig, "fig-tracking-error.png")


def terms():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.4))
    q2 = np.linspace(-np.pi, np.pi, 200)
    Ms = np.array([m.mass(np.array([0.0, x]), P) for x in q2])
    for (i, j), c, lab in (((0, 0), BLUE, "M11 (joint 1 inertia)"), ((0, 1), ORANGE, "M12 (coupling)"), ((1, 1), GREY, "M22 (joint 2 inertia)")):
        a1.plot(np.degrees(q2), Ms[:, i, j], color=c, lw=2, label=lab)
    a1.set_xlabel("elbow angle q2 (deg)")
    a1.set_ylabel("inertia entry (kg m^2)")
    a1.set_title("The inertia depends on the elbow", fontsize=13)
    a1.legend(loc="lower center", fontsize=9)
    a1.grid(alpha=0.3)
    t = np.linspace(0, 1, 400)
    r = m.trajectory(t[:, None])
    inertial = [np.linalg.norm(m.mass(q, P) @ a) for q, a in zip(r[0], r[2])]
    cor = [np.linalg.norm(m.coriolis(q, v, P)) for q, v in zip(r[0], r[1])]
    a2.plot(t, inertial, color=BLUE, lw=2, label="|M(q) * a_d|")
    a2.plot(t, cor, color=ORANGE, lw=2, label="|h(q, v)|  (Coriolis + centripetal)")
    a2.set_xlabel("time along the reference (s)")
    a2.set_ylabel("torque norm (Nm)")
    a2.set_title("Model terms PD has to treat as surprises", fontsize=13)
    a2.legend(loc="upper center", fontsize=9)
    a2.grid(alpha=0.3)
    save(fig, "fig-model-terms.png")


if __name__ == "__main__":
    tracking()
    terms()
