# MuJoCo Hello World

> simulator가 물체를 아주 작은 시간 스텝으로 움직이는 법, 잘못된 스텝이 없던 에너지를 만드는 이유, 그리고 한 줄짜리 해결책을 배웁니다.

**유형:** 만들기   **선수 지식:** 00/01 Python 환경과 numpy   **시간:** 약 15분

## 쉽게 말하면

공을 막대에 매달아 그네처럼 놓아 보세요. 마찰이 없으면 놓은 곳보다 높이 올라가지 않아요.

컴퓨터는 공을 아주 작은 시간 단위로 나눠 움직여요. 한 단계마다 속도를 먼저 바꾸고 공을 옮겨요. 바뀌기 전 속도로 옮기면 단계마다 에너지가 조금씩 더해져서 흔들림이 커져요. 새 속도로 옮기면 해결돼요.

## 핵심 용어

- **Simulation**: 작은 시간 스텝 하나를 여러 번 되풀이해서 물체가 어떻게 움직일지 예측하는 프로그램입니다.
- **Time step (`dt`)**: 한 번에 시간을 얼마나 앞으로 넘기는지입니다. 여기서는 100분의 몇 초입니다.
- **Pendulum**: 막대 끝에 달려 중력으로 흔들리는 추입니다. simulator를 시험하는 가장 간단한 대상입니다.
- **Period**: 한 번 갔다가 돌아오는 데 걸리는 시간입니다.
- **Explicit / semi-implicit Euler**: 스텝을 밟는 두 방법입니다. explicit는 옛 속도로, semi-implicit는 새 속도로 움직입니다.
- **MuJoCo**: 무료 물리 엔진입니다. 우리 반복문과 비교할 완성된 simulator입니다.

## 문제

forum에서 물리 반복문을 가져와 진자를 돌렸습니다. 흔들릴 때마다 조금씩 높이 올라가다가 결국 한 바퀴를 돕니다. 식은 맞아 보이고 틀린 것은 두 줄의 순서뿐입니다.

## 개념

로봇은 실물을 움직이기 전에 simulation으로 시험합니다. 에너지를 지어내는 simulator로 시험하면 이유 없이 실패하는 로봇이 나옵니다. 엔진은 이 상자들을 시간 스텝마다 되풀이합니다.

![물리 한 스텝](../assets/diagram-physics-step.png)

*가속도가 속도를 바꾸고 새 속도가 위치를 움직입니다. 옛 속도로 움직이면 explicit Euler입니다.*

`theta`는 흔들린 각도(radians), `omega`는 각속도, `L`은 막대 길이, `g`는 중력(9.81)입니다. 중력은 속도를 초마다 `-(g/L) sin(theta)`만큼 바꿉니다.

explicit 스텝 하나는 에너지에 약 `1 + (g/L) dt^2`를 곱합니다. 1보다 조금 큰 값입니다. 0.5 rad에서 놓고 10초를 돌리면 semi-implicit는 0.50 rad에 머물고 explicit는 2.46 rad까지 올라갑니다.

![진자 세 개](../assets/clip-example.mp4)

*1.8배 빠르게 재생합니다. 주황색 선은 놓은 높이입니다. 파랑(explicit, `dt` 0.04초)은 선보다 훨씬 올라가고 작고 진한 파랑(explicit, `dt` 0.01초)은 천천히 오르며 초록(semi-implicit)은 선에 머뭅니다.*

![같은 진자를 푸는 두 solver](../assets/diagram-two-solvers.png)

*우리 반복문과 MuJoCo는 같은 주기를 줍니다.*

![스텝 크기 오차](../assets/fig-step-size.png)

*왼쪽은 explicit Euler의 에너지가 올라가는 모습입니다. 오른쪽은 `dt`를 절반으로 줄이면 주기 오차가 약 4분의 1이 되는 모습입니다.*

## 만들기

두 방식의 차이는 어느 `omega`가 각도를 움직이느냐뿐입니다.

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

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-setup-and-tooling/02-mujoco-hello-world -q
python3 phases/00-setup-and-tooling/02-mujoco-hello-world/code/main.py
```

## 실제 도구로 보기

`mujoco_period()`는 MJCF(MuJoCo의 XML 모델 형식)로 같은 진자를 만들고 `mujoco.mj_step`으로 돌립니다. 두 주기는 0.5% 안에서 일치합니다(테스트로 확인). MuJoCo의 기본 `Euler` integrator는 semi-implicit입니다.

출처: https://mujoco.readthedocs.io/en/stable/XMLreference.html

## 결과물

`outputs/skill-sim-sanity-check.md`는 새 simulation을 믿기 전에 주기, 에너지, 스텝 크기를 확인하는 체크리스트입니다.

## 연습 문제

1. `step`에 damping(속도를 줄이는 힘)을 넣고 에너지가 줄어드는지 확인하세요.
2. 주기 오차가 1% 아래로 유지되는 가장 큰 `dt`를 찾으세요.
3. MJCF 문자열의 `L`을 바꾸고 주기가 `sqrt(L)`에 비례하는지 확인하세요.
