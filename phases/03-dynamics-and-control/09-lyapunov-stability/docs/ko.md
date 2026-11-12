# Lyapunov 안정성을 검사로 확인하기

> 안정한 시스템에는 절대 오르지 않는 에너지 같은 수가 있고 그것을 컴퓨터로 시험할 수 있습니다.

**유형:** 만들기   **선수 지식:** 03/04 PID와 튜닝, 03/06 LQR   **시간:** 약 15분

## 쉽게 말하면

그릇 안에서 구르는 구슬은 빨라졌다가 높이 올라가며 느려져요. 마찰로 에너지가 줄어들어서 더 밀어 주지 않으면 더 높은 에너지 상태로 계속 갈 수 없어요. 에너지 같은 양을 보면 구르는 모습 한 번보다 넓게 운동을 살필 수 있어요.

Lyapunov function도 제어 중인 joint에서 이런 역할을 해요. 운동을 따라 그 값이 줄어드는지 확인해요. negative damping이면 값이 커질 수 있지만 목표 각도에서 속도도 정확히
[0](../code/tests/test_lyapunov_stability.py)이면 그대로 멈춰 있어요. 여러 상태를 검사하면 이 실패를 찾을 수 있지만 모든 상태의 안전을 증명하지는 못해요.

## 문제

지금 아는 안정성 시험은 "시뮬레이션했더니 가라앉았다"뿐입니다. 정지 상태에서 시작한 실행은 불안정한 시스템에서도 가만히 있고 한 출발점의 실행은 발산하는 상태 공간의 구석을 놓칩니다. 경로 하나가 아니라 모든 상태를 덮는 시험이 필요합니다.

## 개념

![Lyapunov 시험](../assets/diagram-lyapunov-logic.png)

*V를 고르고 그 기울기의 부호를 확인합니다. 운동 방정식을 풀 필요는 없습니다.*

PD로 제어하는 진자에서는 `V = 1/2 w^2 + (g/l)(1 - cos q) + 1/2 kp q^2`을 잡습니다. 운동에너지, 중력 위치에너지, 스프링의 위치에너지입니다. 운동을 따라 미분하면 `dV/dt = -(c + kd) w^2`이 되고 감쇠를 뺀 항이 모두 사라집니다. 그래서 `dV/dt <= 0`이 모든 곳에서 성립할 조건은 `c + kd >= 0`입니다.

![실행 한 번과 표본 검사](../assets/diagram-lyapunov-sweep.png)

*감쇠가 음수이면 정지 상태에서 시작한 실행은 움직이지 않아 안정해 보입니다. 상태를 훑으면 양의 기울기가 바로 나옵니다.*

![V의 등위선과 화살표](../assets/fig-lyapunov-level-sets.png)

*회색 곡선이 V의 등위선입니다. 파란 화살표는 바깥을 향하지 않고 주황 화살표는 바깥을 향합니다. `kd = -1`이면 거의 모든 화살표가 주황입니다.*

![늦게 도착한 속도 신호](../assets/fig-lyapunov-delay.png)

*게인은 같고 `kd = 5`지만 컨트롤러가 속도를 늦게 봅니다. 300 ms에서는 V가 줄지 않고 올라갑니다.*

## 만들기

```python
grad = np.array([(V(x + h*e, p) - V(x - h*e, p)) / (2*h) for e in np.eye(2)])
vdot = grad @ f(x, p)          # dV/dt along the motion
```

`check()`가 상태를 뽑아 가장 큰 `vdot`과 그 위치를 돌려줍니다. 테스트는 `V`가 양수인지, `vdot`이 `-(c + kd) w^2`과 같은지, 안정한 게인이 통과하는지, 음의 감쇠가 잡히는지, 늦은 속도가 V를 올리는지 확인합니다. 표본 검사는 반례를 찾을 뿐이고 반례가 없다는 증명은 아닙니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/09-lyapunov-stability -q
python3 phases/03-dynamics-and-control/09-lyapunov-stability/code/figure.py
```

## 실제 도구로 보기

운용 범위 안에서 SciPy의 `minimize`로 `-vdot`을 최소화해 반례를 탐색합니다. 그 위치의 `vdot` 최대값을 보고하고 표본 검사와 비교하세요. 증명이 필요하면 SOS나 SMT 도구가 부호를 확인해야 합니다.

## 결과물

`outputs/skill-lyapunov-check.md`는 안정성 주장을 후보 V와 표본 검사로 바꿉니다.

## 연습 문제

1. `kp = 0`으로 두고 원점에서 먼 곳에서 V의 부호가 어떻게 되는지 설명하세요.
2. `kd = 5`가 처음으로 가라앉지 못하는 지연 값을 찾으세요.
3. 마찰 항 `c |w| w`를 더하고 `vdot`을 손으로 다시 구하세요.
