# 모터와 기어박스 (Motor and Gearbox)

> 기어박스가 무거운 부하를 모터에게 거의 가볍게 느껴지게 하는 이유를 배웁니다.

**유형:** 만들기   **선수 지식:** 03/02 중력 보상   **시간:** 약 15분

## 쉽게 말하면

작은 모터가 기어박스를 거쳐 무거운 flywheel(쇠바퀴)을 돌려야 해요. 기어박스 덕분에 flywheel은 모터 축보다 훨씬 느리게 돌아요. 그래서 모터는 flywheel을 실제보다 훨씬 가볍게 느껴요.

모터는 빨리 돌수록 자기 전원에 맞서는 전압도 만들어서 밀어 주는 힘이 약해져요.

## 핵심 용어

- **Torque**: 물체를 비트는 힘입니다. 모터가 축에 가하는 힘이 이것입니다.
- **Back-EMF**: 도는 모터가 자기 전원에 맞서 만드는 전압입니다. 전류와 미는 힘을 줄입니다.
- **Inertia**: 물체를 돌리기 어려운 정도입니다. 무거운 flywheel은 값이 큽니다.
- **Gear ratio (`N`)**: 출력이 한 바퀴 돌 때 모터가 도는 바퀴 수입니다. 토크는 `N`배 커지고 속도는 `N`분의 1이 됩니다.
- **Stall torque**: 모터를 붙잡아 멈춰 둘 때 내는 힘으로 가장 큰 값입니다.
- **Drive**: 모터에 전기를 보내고 제어하는 전자회로입니다.

## 문제

로봇 팔은 무거운 공구를 달기 전과 후에 똑같이 움직입니다. 100:1 기어박스가 빈 팔에서 튜닝한 drive에게서 부하를 가리기 때문입니다.

## 개념

이것으로 관절에 모터가 얼마나 필요한지, 부하가 바뀌어도 한 번의 튜닝이 왜 통하는지 알 수 있습니다.

![모터의 전압과 전류와 토크와 back-EMF](../assets/diagram-motor-chain.png)

*빨리 돌수록 back-EMF가 커져서 토크가 줄어듭니다.*

`V`는 전원 전압, `w`는 축 속도, `R`은 코일 저항, `kt`는 토크 상수(전류 1 A당 토크)입니다. 전류는 `(V - kt*w) / R`이고 토크는 `kt * 전류`입니다.
토크는 멈춰 있을 때(`w = 0`)의 stall torque에서 시작해 `V / kt`에서 0이 될 때까지 직선으로 줄어듭니다.

![flywheel 관성을 N의 제곱으로 나눈 모습](../assets/diagram-reflected-inertia.png)

*flywheel의 관성을 N의 제곱으로 나누면 rotor가 지배적으로 남습니다.*

감속비 `N`인 기어박스는 토크를 `N`배 하고 속도를 `N`으로 나눕니다. 도는 에너지는 속도의 제곱에 비례하므로 모터는 flywheel을 `J_L / N^2`만큼으로 느낍니다.

rotor 관성 `J_r = 2e-5`와 flywheel 관성 `J_L = 2e-3`(kg m^2)을 예로 듭니다. `N = 1`이면 모터는 자기 관성의 101배를 느껴서 최종 속도의 63%에 이르는 데 8 ms 대신 0.81초가 걸립니다.
`N = 100`이면 1.01배를 느끼고 8.08 ms가 걸립니다.

![N = 1과 N = 100에서 같은 flywheel](../assets/clip-example.mp4)

*왼쪽(N = 1)은 rotor가 기어갑니다. 오른쪽(N = 100)은 rotor가 달립니다.*

![토크-속도 직선과 기동 곡선](../assets/fig-motor-gearbox.png)

*왼쪽은 기어박스가 직선을 구부리지 않고 옮긴다는 것을 보여 줍니다. 오른쪽은 N = 100에서 부하가 있을 때와 없을 때의 곡선이 겹친다는 것을 보여 줍니다.*

## 만들기

부하 토크는 `N`으로 나뉘어 들어옵니다.

```python
def motor_torque(w, kt, R, V):
    return kt * (V - kt * np.asarray(w, float)) / R

def load_at_motor(J_load, N):
    return J_load / N**2

def inertia_sensitivity(J_rotor, J_load, N):
    return (J_rotor + load_at_motor(J_load, N)) / J_rotor
```

`spin_up()`은 `J * dw/dt = motor_torque(w) - tau_load / N`을 적분합니다. sensitivity가 1.0이면 drive가 부하를 보지 못한다는 뜻입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/01-motor-and-gearbox -q
python3 phases/04-actuators-and-sensors/01-motor-and-gearbox/code/figure.py
```

## 실제 도구로 보기

MuJoCo 문서에는 이 항들로 이루어진 DC motor actuator가 있습니다.

출처 (2026년 11월 9일 접속):

- [MuJoCo DC motor model](https://mujoco.readthedocs.io/en/latest/_static/dcmotor.pdf)
- [Faulhaber DC motor calculations](https://www.faulhaber.com/en/know-how/tutorials/dc-motor-tutorial-motor-calculations-for-coreless-brush-dc-motors/)

## 결과물

`outputs/skill-motor-gearbox-check.md`는 모터 상수와 감속비를 받아 stall torque와 부하가 보이는 정도를 계산합니다.

## 연습 문제

1. 점성 마찰 `b*w`를 넣고 새 정상 속도를 구하세요.
2. 부하가 모터 쪽 관성에 5%만 더하게 되는 감속비 `N`을 구하세요.
3. 기어박스 효율을 1보다 낮게 넣으세요.
