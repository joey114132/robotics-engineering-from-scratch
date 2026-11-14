# Kalman Filter

> 모델과 잡음 낀 센서가 어긋날 때 Kalman gain이 센서 쪽으로 얼마나 움직일지를 정하고 결과가 아직 얼마나 틀렸는지도 알려 줍니다.

**유형:** 만들기   **선수 지식:** 07/01 Bayes Filter   **시간:** 약 15분

## 쉽게 말하면

장난감 자동차가 도로를 달리고 위치 센서가 자동차의 위치를 알려 줘요. 그런데 센서 값은 매번 몇 미터쯤 틀려요. 자동차가 대략 얼마나 빠른지도 알아서 다음 위치를 예측할 수 있어요. 센서가 많이 흔들리면 추정값을 센서 쪽으로 조금만 옮겨요. 예측이 더 불확실하면 더 많이 옮겨요.

Kalman gain이 바로 이 균형이에요. filter는 추정값이 아직 얼마나 불확실한지, 곧 covariance도 함께 계산해요.

## 문제

위치 센서가 읽을 때마다 2 m쯤 틀립니다. 원본 출력을 그리면 로봇이 떠는 것처럼 보입니다. 최근 몇 개를 평균하면 떨림은 사라지지만 방향을 바꿀 때마다 뒤처집니다.

## 개념

![Kalman 한 사이클](../assets/diagram-kalman-loop.png)

*모션 모델로 predict하고 센서값으로 correct합니다. 그 결과가 다음 사이클로 들어갑니다.*

상태 `x`는 `[position, velocity]`입니다. `P`는 그 분산, 곧 퍼짐의 제곱이라서 불확실성 2 m는 `P = 4`입니다.

predict는 `x = F x`, `P = F P F^T + Q`입니다. `F`는 상태를 한 스텝 옮기고(위치 + 속도 * 시간) `Q`는 실제 속도가 조금 바뀔 수 있어서 더해지는 불확실성입니다.

센서값 `z = H x + noise`는 위치만 보고(`H`가 위치만 골라냅니다) 잡음 분산은 `R`입니다. correct는 `x = x + K (z - H x)`이므로 추정값은 `K`에 놀람 `z - H x`를 곱한 만큼 움직입니다.

가장 좋은 `K = P H^T (H P H^T + R)^-1`은 불확실성을 가장 적게 남기고 그때의 `P`는 `P = (I - K H) P (I - K H)^T + K R K^T`(Joseph 형태)입니다.

위치 하나만 보면 `K = P / (P + R)`입니다. 0에서 `P = 4`로 시작하고 센서값이 3 m라고 해 봅시다. `R = 4`이면 gain은 `K = 4 / (4 + 4) = 0.5`라서 추정값은 1.5 m 움직이고 `P`는 2로 줄어듭니다.

잡음이 6 m인 센서는 `R = 36`이라서 `K = 4 / 40 = 0.1`이고 추정값이 0.3 m만 움직입니다.

![같은 센서값, 센서 두 종류](../assets/clip-example.mp4)

*호박색 센서값으로 미끄러지는 핀을 보세요. 파란 도로는 센서 잡음이 6 m로 커서 핀이 거의 안 움직입니다. 초록 도로는 절반쯤 움직이고 ±2 sigma 띠(`sigma = sqrt(P)`, 미터로 나타낸 퍼짐)가 더 많이 줄어듭니다.*

![gain은 신뢰를 나누는 다이얼입니다](../assets/diagram-kalman-trust.png)

*센서 잡음이 크면 K가 작아져서 filter는 모델을 따릅니다. 모델이 불확실하면 K가 커져서 센서를 따릅니다.*

![추정값과 실제 오차](../assets/fig-kalman-band.png)

*왼쪽은 한 번의 실행이고 추정값이 2-sigma 띠 안에 있습니다. 오른쪽은 4000번 실행했을 때 오차가 원본 2.0 m의 절반인 1.0 m 근처에 가라앉아 `sqrt(P)`와 맞는 모습입니다.*

## 만들기

```python
def gain(P, H, R):
    return P @ H.T @ np.linalg.inv(H @ P @ H.T + R)

x, P = F @ x, F @ P @ F.T + Q        # predict
K = gain(P, H, R)
x = x + K @ (z[None, :] - H @ x)     # update
P = (np.eye(2) - K @ H) @ P
```

테스트는 세 가지를 확인합니다. 다른 `K`를 쓰면 Joseph trace가 커지는지, 4000번 실행이 `P`와 맞는지, 오차의 약 95%가 2 sigma 안에 드는지입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/02-kalman-filter -q
```

## 실제 도구로 보기

ROS의 `robot_localization`에는 `ekf_localization_node`가 들어 있습니다. extended Kalman filter입니다.

SciPy의 `solve_discrete_are`는 수렴한 `P`를 줍니다.

출처: robot_localization state estimation nodes, https://docs.ros.org/en/melodic/api/robot_localization/html/state_estimation_nodes.html (2026년 11월 9일 확인).

## 결과물

`outputs/skill-kalman-filter-check.md`는 filter에서 `Q`, `R`, `P`를 잘못 잡아 조용히 틀어지는 흔한 실수를 검토합니다.

## 연습 문제

1. `R_STD`를 두 배로 올리고 실행하기 전에 수렴한 `sqrt(P)`가 오를지 내릴지 예측하세요.
2. `R`을 열 배 작게 잡고 2-sigma 안에 드는 비율을 95%와 비교하세요.
3. `SA`를 0으로 두고 `K`가 0으로 줄어 filter가 센서를 무시하게 되는 것을 보세요.
