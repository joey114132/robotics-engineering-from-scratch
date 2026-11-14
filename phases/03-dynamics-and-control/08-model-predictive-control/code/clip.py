# 레슨 03/08 클립: 입력 한계 0.5 에서 4 m 떨어진 정지선으로 가는 자동차 둘. 파란 차는 잘린 LQR 이라 늦게 브레이크를 밟아 넘치고, 초록 차는 MPC 라 앞을 미리 보고 멈춘다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import numpy as np

import kit

m = kit.lesson_main(__file__)
DT, N, S, UMAX, SPEED, H, CS = 0.1, 120, 0.55, 0.5, 2.0, 20, 1.6      # the lesson's step and 12 s run, played at 2x; 1 m is drawn as 0.55 m; plan length 20 steps; the cars are drawn 1.6 times larger
A, B = m.double_integrator(DT)
Q, R = np.diag([1.0, 0.1]), np.array([[0.1]])
x0 = np.array([4.0, 0.0])
K, _ = m.riccati(A, B, Q, R)
x, clipped = x0.copy(), []
for _ in range(N):                                           # the clipped LQR of the lesson's figure: u = -K x, then cut at the limit
    clipped.append(x[0])
    x = A @ x + B[:, 0] * np.clip(-(K @ x)[0], -UMAX, UMAX)
log = []
mpc = m.simulate(x0, N, A, B, Q, R, H, UMAX, plan_log=log)[0][:, 0]
Phi, Gam = m.prediction(A, B, H)

sc = kit.setup(N * DT / SPEED)
kit.stripe(-3.6, 1.4, -1.0, 1.0, "road")
kit.stripe(-0.03, 0.03, -1.0, 1.0, "white", z=0.004)
kit.box("post", (0.04, 0.04, 0.6), (0.0, 1.12, 0.3), "dark", bevel=0)
kit.cyl("sign", 0.17, 0.03, (0.0, 1.1, 0.68), "y", "red", segments=8)
cars = {"blue": (kit.car("lqr", "blue", CS), 0.55, np.array(clipped)), "green": (kit.car("mpc", "green", CS), -0.55, mpc)}
beads = [kit.ball("plan", 0.045, colour=kit.ghost("green", 0.75)) for _ in range(H)]     # where the MPC car expects to be over the next 2 s
for f in range(sc.frame_start, sc.frame_end + 1):
    k = min(int((f - 1) / 24 * SPEED / DT), N - 1)
    for (root, wheels, _), y, pos in cars.values():
        kit.drive(root, wheels, f, -S * pos[k] - 0.3 * CS, y, radius=0.09 * CS)
    xk, U = log[k]
    for b, p in zip(beads, (Phi @ xk + Gam @ U)[0::2]):
        kit.key(b, f, loc=(-S * p, -0.55, 0.05))
kit.camera((-1.1, -4.8, 3.0), (-1.1, 0.05, 0.1), lens=36)
kit.render(__file__)
