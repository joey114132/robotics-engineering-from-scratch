# 레슨 04/01: DC 모터 토크-속도 직선, 기어 반사 관성, 감속비가 부하 변화를 가리는 정도
import numpy as np
# SI units: torque constant kt (Nm/A) equals the back-EMF constant (V s/rad), so one number serves both.


def motor_torque(w, kt, R, V):
    """Torque at motor speed w: current is (V - back-EMF) / R and torque is kt * current."""
    return kt * (V - kt * np.asarray(w, float)) / R


def stall_torque(kt, R, V):
    return motor_torque(0.0, kt, R, V)


def no_load_speed(kt, R, V):
    return V / kt


def gear_output(tau_m, w_m, N, eta=1.0):
    """Output torque and speed of a gearbox with ratio N (efficiency eta only costs torque)."""
    return N * eta * tau_m, w_m / N


def rotor_at_output(J_rotor, N):
    """Rotor inertia as felt on the output shaft: kinetic energy goes with speed squared."""
    return J_rotor * N**2


def load_at_motor(J_load, N):
    """Load inertia as felt on the motor shaft."""
    return J_load / N**2


def inertia_sensitivity(J_rotor, J_load, N):
    """Motor-side inertia with the load attached, divided by without it. 1.0 = the motor cannot see the load."""
    return (J_rotor + load_at_motor(J_load, N)) / J_rotor


def time_constant(N, J_rotor, J_load, kt, R, V):
    """Electromechanical time constant on the motor shaft: J_total * R / kt^2 (V does not matter)."""
    return (J_rotor + load_at_motor(J_load, N)) * R / kt**2


def spin_up(N, J_rotor, J_load, tau_load, T, dt, kt, R, V):
    """Motor speed after a voltage step. Output-side load torque arrives at the motor divided by N."""
    J = J_rotor + load_at_motor(J_load, N)
    n = int(round(T / dt))
    w = np.zeros(n + 1)
    for k in range(n):
        w[k + 1] = w[k] + dt * (motor_torque(w[k], kt, R, V) - tau_load / N) / J
    return np.arange(n + 1) * dt, w


if __name__ == "__main__":
    M = dict(kt=0.05, R=1.0, V=24.0)
    for N in (1.0, 10.0, 100.0):
        print(N, inertia_sensitivity(2e-5, 2e-3, N))
