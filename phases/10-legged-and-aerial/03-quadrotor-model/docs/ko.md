# 쿼드로터 모델

> 쿼드로터는 옆으로 직접 밀 수 없습니다. 먼저 기울고 그 기울기가 추력을 옆 방향 힘으로 바꿉니다.

**유형:** 만들기   **선수 지식:** 10/01 도립진자와 ZMP   **시간:** 약 15분

## 문제

드론에 오른쪽 1 m 이동을 명령하면 처음에는 명령을 무시하는 것처럼 보입니다. 그러다 기울고 흘러가면서 높이도 잃습니다. 입력이 총 추력과 토크 하나뿐인데 움직여야 할 것은 셋이기 때문입니다.

## 개념

![기울기로 나뉘는 하나의 추력](../assets/diagram-thrust-split.png)

*추력은 항상 몸체 축을 따라 향합니다. pitch `theta`가 그중 얼마가 위로 가고 얼마가 옆으로 가는지 정합니다.*

상태가 `x, z, theta`이고 입력이 `T`와 `tau`인 평면 모델입니다.

`m x'' = T sin(theta)`, `m z'' = T cos(theta) - m g`, `I theta'' = tau`.

`theta = 0`이고 `T = m g`이면 모든 가속도가 0이므로 호버 추력은 `m g`입니다. 같은 추력으로 `theta`만큼 기울이면 높이 가속도는 `g (cos(theta) - 1)`이고 음수입니다.

높이를 유지하려면 `T = m g / cos(theta)`가 필요하고 이때 옆 방향 가속도는 `g tan(theta)`입니다.

![토크에서 위치까지](../assets/diagram-torque-to-position.png)

*토크는 적분 네 번을 거쳐 위치에 닿으므로 토크 계단은 작은 각도에서 `x = g tau t^4 / (24 I)`가 됩니다.*

![추력 계단과 토크 계단](../assets/fig-tilt-then-move.png)

*왼쪽은 추력을 10% 더하면 위로만 올라가는 모습입니다. 오른쪽은 0.002 Nm 토크가 0.27초에 1도 기울이지만 1 cm 이동은 0.47초에야 일어나는 모습입니다.*

## 만들기

```python
def deriv(s, T, tau, m, I, g=G):
    th = s[2]
    return np.array([s[3], s[4], s[5], T*np.sin(th)/m, T*np.cos(th)/m - g, tau/I])
```

상태는 `[x, z, theta, vx, vz, omega]`입니다. `simulate()`는 제어 함수를 받아 RK4로 적분합니다. 예제는 작은 기체를 가정한 임의의 값 `m = 0.5 kg`, `I = 0.004 kg m^2`를 씁니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/10-legged-and-aerial/03-quadrotor-model -q
python3 phases/10-legged-and-aerial/03-quadrotor-model/code/main.py
```

## 실제 도구로 보기

마지막 테스트가 같은 식을 SciPy의 `solve_ivp`로 적분해 최종 상태를 비교합니다. 실제 기체는 mixer로 `T`와 `tau`를 모터 네 개의 속도로 바꿉니다. 이 부분은 이 레슨의 범위 밖입니다.

## 결과물

`outputs/skill-quadrotor-model-check.md`는 쿼드로터 모델이나 제어기에서 호버 추력, 기울기 결합, 단위를 검토합니다.

## 연습 문제

1. `T = m g / cos(theta)`로 30도 기울였을 때 옆 방향 가속도를 구하세요.
2. 0.004 Nm 토크가 10도에 이르는 시간을 구하세요.
3. 항력 `-c vx`를 넣고 새로운 정상 속도를 구하세요.
