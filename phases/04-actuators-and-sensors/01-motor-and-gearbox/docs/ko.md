# 모터와 기어박스 (Motor and Gearbox)

> 모터는 빨리 돌수록 약해지는 토크 원천이고 기어박스는 부하를 모터에게 거의 보이지 않게 만듭니다.

**유형:** 만들기   **선수 지식:** 03/02 중력 보상   **시간:** 약 15분

## 쉽게 말하면

작은 모터가 기어박스를 거쳐 무거운 flywheel(무거운 쇠바퀴)을 돌려야 해요. 기어박스는 flywheel이 모터 축보다 훨씬 느리게 돌게 해요. 도는 물체의 에너지는 속도의 제곱에 비례해서 느린 flywheel에는 에너지가 거의 담기지 않아요.

그래서 모터는 flywheel이 실제보다 훨씬 가볍다고 느껴요. 다만 함정이 하나 있어요. 모터는 빨리 돌수록 자기 전원에 맞서는 전압을 더 만들어요. 그러면 전류가 줄어서 밀어 주는 힘도 약해져요.

## 문제

관절 모터에 100:1 기어박스를 답니다. 팔이 비어 있을 때 drive(모터에 전기를 보내는 전자회로)를 튜닝합니다. 나중에 팔이 무거운 공구를 들어도 관절은 똑같이 동작합니다. drive는 팔 끝에 무엇이 달려 있는지 알 수 없기 때문입니다.

## 개념

전원 전압에서 토크(비트는 힘)까지 화살표를 따라가 보세요. 그다음 빨간 상자가 전류로 되돌아가는 것을 보세요.

![모터의 전압과 전류와 토크와 back-EMF](../assets/diagram-motor-chain.png)

*빨리 돌수록 back-EMF(모터가 전원에 맞서 만드는 전압)가 커져서 전류와 토크가 줄어듭니다.*

여기서 `V`는 전원 전압, `w`는 축 속도, `R`은 코일 저항, `kt`는 토크 상수(전류 1 A당 토크)입니다. 전류는 `(V - kt*w) / R`이고 토크는 `kt * 전류`입니다. 그래서 토크는 멈춰 있을 때(`w = 0`)의 stall torque에서 시작해 무부하 속도 `V / kt`에서 0이 될 때까지 직선으로 줄어듭니다.

이제 기어박스입니다. flywheel의 관성이 작아지는 것을 보세요.

![flywheel 관성을 N의 제곱으로 나눈 모습](../assets/diagram-reflected-inertia.png)

*flywheel의 관성을 N의 제곱으로 나누면 rotor가 지배적으로 남습니다.*

감속비 `N`인 기어박스는 토크를 `N`배 하고 속도를 `N`으로 나눕니다. 관성 `J_L`(flywheel을 돌리기 어려운 정도)이 속도 `w/N`로 돌 때 도는 에너지는 `J_L*(w/N)^2/2`이고 이것은 관성 `J_L / N^2`이 속도 `w`로 돌 때의 에너지와 같습니다.
그래서 모터가 느끼는 값은 `J_L / N^2`입니다.

rotor(모터의 도는 부분) 관성 `J_r = 2e-5`이고 flywheel 관성 `J_L = 2e-3`(kg m^2, 2e-5는 0.00002)이라고 합니다.

`N = 1`이면 모터는 `2e-3 + 2e-5`, 즉 rotor 관성의 101배를 느껴서 최종 속도의 63%에 이르는 데 8 ms 대신 0.81초가 걸립니다. `N = 100`이면 `2e-5 + 2e-7`, 즉 1.01배를 느끼고 8.08 ms가 걸립니다.

![N = 1과 N = 100에서 같은 flywheel](../assets/clip-example.mp4)

*왼쪽(N = 1, 파랑)은 rotor가 기어갑니다. 오른쪽(N = 100, 초록)은 rotor가 달리고 flywheel은 100배 느리게 돕니다.*

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

MuJoCo 문서에는 이 항들로 이루어진 DC motor actuator가 있습니다. `kt`, `R`, rotor 관성을 datasheet와 비교하세요.

출처 (2026년 11월 9일 접속):

- [MuJoCo DC motor model](https://mujoco.readthedocs.io/en/latest/_static/dcmotor.pdf)
- [Faulhaber DC motor calculations](https://www.faulhaber.com/en/know-how/tutorials/dc-motor-tutorial-motor-calculations-for-coreless-brush-dc-motors/)

## 결과물

`outputs/skill-motor-gearbox-check.md`는 모터 상수와 감속비를 받아 stall torque, 무부하 속도, 부하가 보이는 정도를 계산합니다.

## 연습 문제

1. 점성 마찰 `b*w`를 넣고 새 정상 속도를 구하세요.
2. 부하가 모터 쪽 관성에 5%만 더하게 되는 감속비 `N`을 구하세요.
3. 효율을 1보다 낮게 넣고 출력 토크는 줄지만 속도는 그대로임을 보이세요.
