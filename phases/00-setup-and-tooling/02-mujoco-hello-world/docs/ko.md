# MuJoCo Hello World

> simulator는 `dt`마다 힘을 새 상태로 바꾸는 반복문입니다. 믿기 전에 하나를 직접 써 보세요.

**유형:** 만들기   **선수 지식:** 00/01 Python 환경과 numpy   **시간:** 약 15분

## 문제

forum에서 가져온 물리 반복문으로 진자를 돌렸더니 한 번 흔들릴 때마다 조금씩 높이 올라가다가 결국 한 바퀴를 돕니다. 프로그램은 멈추지 않았고 식도 맞아 보입니다. 틀린 것은 시간 스텝 안에서 두 줄의 순서뿐입니다.

## 개념

![물리 한 스텝](../assets/diagram-physics-step.png)

*가속도가 속도를 바꾸고 새 속도가 위치를 움직입니다. 옛 속도로 위치를 움직이면 explicit Euler입니다.*

물리 엔진은 이 스텝을 반복합니다. 진자가 가장 작은 예입니다. 식은 `omega' = -(g/L) sin(theta)`이고 작게 흔들 때 주기는 `2 pi sqrt(L/g)`입니다.

![같은 진자를 푸는 두 solver](../assets/diagram-two-solvers.png)

*진자 하나를 우리 반복문과 MuJoCo로 두 번 풀고 주기를 비교합니다.*

![에너지와 스텝 크기 오차](../assets/fig-step-size.png)

*왼쪽은 explicit Euler가 흔들릴 때마다 에너지를 더하는 모습입니다. 오른쪽은 `dt`를 절반으로 줄이면 주기 오차가 약 4분의 1이 되는 모습입니다.*

## 만들기

스텝 하나와 반복문입니다. 두 방식의 차이는 어느 `omega`가 각도를 움직이느냐뿐입니다.

```python
def step(theta, omega, dt, L=1.0, scheme="semi"):
    omega_new = omega - dt * (G / L) * np.sin(theta)
    return theta + dt * (omega_new if scheme == "semi" else omega), omega_new

def simulate(theta0, dt, seconds, L=1.0, scheme="semi"):
    theta, omega, out = theta0, 0.0, [theta0]
    for _ in range(int(round(seconds / dt))):
        theta, omega = step(theta, omega, dt, L, scheme)
        out.append(theta)
    return np.array(out)
```

`measure_period`는 위로 올라가는 영점 통과를 찾고 스텝 안에서 보간합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-setup-and-tooling/02-mujoco-hello-world -q
python3 phases/00-setup-and-tooling/02-mujoco-hello-world/code/main.py
```

## 실제 도구로 보기

`mujoco_period()`는 inline MJCF 문자열로 같은 진자를 만들고 `mujoco.mj_step`을 부릅니다.

주기는 우리 값과 0.5% 안에서 일치합니다(테스트가 확인하고 MuJoCo가 없으면 건너뜁니다). MuJoCo XML 레퍼런스에서 `integrator`의 기본값은 `Euler`이고 semi-implicit Euler라고 설명합니다. 문서는 `implicitfast`도 권합니다.

출처: https://mujoco.readthedocs.io/en/stable/XMLreference.html

## 결과물

`outputs/skill-sim-sanity-check.md`는 새 simulation을 믿기 전에 주기, 에너지, 스텝 크기를 확인하는 체크리스트입니다.

## 연습 문제

1. `step`에 damping을 넣고 에너지가 줄어드는지 확인하세요.
2. 주기 오차가 1% 아래로 유지되는 가장 큰 `dt`를 찾으세요.
3. MJCF 문자열의 `L`을 바꾸고 주기가 `sqrt(L)`에 비례하는지 확인하세요.
