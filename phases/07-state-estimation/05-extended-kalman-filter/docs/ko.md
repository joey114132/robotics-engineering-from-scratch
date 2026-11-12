# 확장 칼만 필터 (Extended Kalman Filter)

> 모델을 현재 추정값에서 선형화하고 그 위에서 Kalman filter를 돌립니다. 추정값이 진짜 값에 충분히 가까울 때만 통합니다.

**유형:** 만들기   **선수 지식:** 07/02 칼만 필터, 08/01 차동 구동과 오도메트리   **시간:** 약 15분

## 쉽게 말하면

운동장에서 내가 향한 방향을 짐작하고 나무까지의 거리와 방향으로 위치를 찾아 보세요. 조금 걸었을 때 측정값이 어떻게 바뀔지에 대한 예측은 내가 어디 있다고 생각하는지에 따라 달라요. heading을 크게 잘못 짐작하면 그럴듯한
보정이 또 다른 실수가 될 수 있어요.

extended Kalman filter는 진짜 상태를 모르므로 현재 추정값에서 운동과 측정을 linearisation해요. 이 국소 근사는 추정값이 실제와 멀면 어긋날 수 있어요. 실제 오차가 커지는데도 filter는 불확실성이
줄었다고 보고할 수 있어요.

## 문제

07/02의 Kalman filter는 `x' = F x` 꼴을 요구합니다. 회전하는 로봇은 heading이 `cos`와 `sin` 안에 들어 있어서 상수 `F`가 없습니다.

그래도 landmark 측정값을 넣어 보면 시작이 좋을 때는 잘 됩니다. 하지만 heading 추정이 1 rad 틀렸고 landmark가 하나뿐이면 필터는 공분산이 작다고 보고하면서 엉뚱한 곳으로 갑니다.

## 개념

![EKF 한 사이클](../assets/diagram-ekf-loop.png)

*진짜 상태를 모르므로 두 Jacobian 모두 현재 추정값에서 계산합니다.*

상태는 `[x, y, heading]`이고 로봇은 속도 `v`와 회전 속도 `w`로 움직입니다.

운동은 `f(x, u)`이고 `F`는 그 편미분 행렬입니다. 위치를 아는 landmark는 range와 bearing `h(x)`를 주고 그 Jacobian이 `H`입니다. 공분산은 `P = F P F^T + Q`로 예측하고 `H`를 쓴 Kalman update로 보정합니다. bearing 차이는 `[-pi, pi]`로 wrap해야 합니다.

![나쁜 선형화점은 스스로를 키웁니다](../assets/diagram-ekf-spiral.png)

*heading이 틀리면 Jacobian이 틀리고 보정이 틀려서 heading이 더 틀어집니다.*

일관성은 NEES `e^T P^-1 e`로 잽니다. 여러 번 돌려 평균하면 상태 차원인 3이 되어야 합니다.

![한 번의 실행과 초기 heading 오차에 따른 NEES](../assets/fig-ekf-run.png)

*왼쪽은 EKF가 진짜 경로를 따라가고 dead reckoning은 휘어지는 모습입니다. 오른쪽은 landmark가 네 개면 NEES가 3 근처에 머물고 하나면 약 4에서 수백까지 커지는 모습입니다.*

## 만들기

```python
def jac_h(x, lm):
    dx, dy = lm - x[:2]
    q, r = dx*dx + dy*dy, np.hypot(dx, dy)
    return np.array([[-dx/r, -dy/r, 0], [dy/q, -dx/q, -1]])

H = jac_h(x, lm)                       # at the estimate
K = P @ H.T @ np.linalg.inv(H @ P @ H.T + R)
y = z - h(x, lm); y[1] = wrap(y[1])
x = x + K @ y
```

테스트는 두 Jacobian을 유한차분과 비교합니다. 시드 150개에서 NEES가 3 근처인지도 봅니다. 또 landmark 하나와 1.5 rad heading 오차에서 NEES가 20배 넘게 커지는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/05-extended-kalman-filter -q
python3 phases/07-state-estimation/05-extended-kalman-filter/code/main.py
```

## 실제 도구로 보기

ROS의 `robot_localization`은 바로 이 예측과 보정 순환을 하는 EKF 노드를 제공합니다. ROS 2 브랜치에서는 `ekf_node`이고 예전 ROS 1 문서에서는 `ekf_localization_node`입니다. 이 레슨의 NEES 검사와 공분산 동작을 비교해 보세요.

출처는 robot_localization의 state estimation nodes 문서(https://docs.ros.org/en/melodic/api/robot_localization/html/state_estimation_nodes.html, 2026년 11월 9일 확인)와 패키지 `CMakeLists.txt`의 `ekf_node` 타깃(https://github.com/cra-ros-pkg/robot_localization, 2026년 11월 10일 확인)입니다.

## 결과물

`outputs/skill-ekf-consistency-check.md`는 EKF의 잘못된 Jacobian, wrap 안 된 각도, 과신하는 공분산을 점검합니다.

## 연습 문제

1. `jac_f`에서 마이너스 부호를 빼 보고 NEES를 보세요.
2. landmark 하나인 경우에 두 번째를 더하고 여전히 발산하는 가장 작은 heading 오차를 찾으세요.
3. `Q`를 4배로 키우고 NEES를 3과 비교하세요.
