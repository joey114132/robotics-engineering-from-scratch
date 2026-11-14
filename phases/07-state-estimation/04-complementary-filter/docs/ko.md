# 상보 필터 (Complementary Filter)

> gyro는 빠른 변화에는 맞고 오래 두면 틀립니다. 가속도계는 그 반대입니다. time constant 하나가 언제 누구를 믿을지 정합니다.

**유형:** 만들기   **선수 지식:** 07/03 IMU 적분과 Drift   **시간:** 약 15분

## 쉽게 말하면

평평한 판이 기둥 위에 있고 그 위에 센서가 있어요. gyro는 회전 속도를 재요. 그 값을 더하면 빠른 기울기 변화는 부드럽게 따라가지만 작고 일정한 오차 때문에 각도가 서서히 어긋나요. 가속도계는 gravity를 느껴서 기울기를 바로 알려 주지만 값이 떨려요.

complementary filter는 빠른 변화는 gyro에서 가져오고 느린 평균은 가속도계에서 가져와요. time constant는 gyro를 얼마나 오래 믿을지 정해요. 길면 떨림은 줄지만 어긋남이 늘고 짧으면 그 반대예요.

## 문제

가속도계만으로 구한 기울기는 너무 떨려서 균형 제어기가 같이 흔들립니다. 적분한 gyro는 매끄럽지만 서서히 멀어져서 똑바로 서 있는데도 기울었다고 믿게 됩니다.

## 개념

![센서 둘, 약점 둘](../assets/diagram-comp-split.png)

*gyro는 high-pass(빠른 변화만 남김)에, 가속도계는 low-pass(느린 평균만 남김)에 통과시킨 뒤 더합니다.*

한 스텝마다 `theta = a (theta + gyro dt) + (1 - a) acc`이고 `acc`는 가속도계로 구한 기울기입니다. 가중치는 `a = tau / (tau + dt)`이고 `tau`는 time constant, `dt`는 스텝 간격입니다.

필터로 보면 가속도계 경로는 `1 / (1 + j w tau)`이고 gyro 경로는 `j w tau / (1 + j w tau)`입니다. `w`는 움직임의 주파수이고 `j`는 타이밍을 나타냅니다.

둘의 합은 정확히 1이므로 진짜 기울기는 그대로 통과합니다. 두 경로는 `1 / (2 pi tau)` Hz에서 만나고 그 지점에서 각각의 gain은 `1 / sqrt(2)`이지만 타이밍이 다릅니다.

![세 추정값과 crossover](../assets/fig-tilt-estimates.png)

*왼쪽은 `tau = 0.40 s`일 때 합친 기울기가 진짜 값 위에 있는 모습입니다. 오른쪽은 crossover가 0.40 Hz이며 `tau`가 아니라 주파수라는 점을 보여 줍니다. 그 아래에서는 가속도계를, 위에서는 gyro를 믿습니다.*

gyro는 약 `tau`초 동안 믿으므로 일정한 bias `b`가 쌓여 정확히 `tau b`의 정상상태 오차가 남습니다.

퍼짐이 `s`인 가속도계 잡음은 `s^2 (1 - a) / (1 + a)`의 분산을 남기고 이는 `dt`가 작으면 약 `s^2 dt / (2 tau)`입니다.

두 오차의 제곱합 `(tau b)^2 + s^2 dt / (2 tau)`를 최소로 만들면 `tau^3 = s^2 dt / (4 b^2)`가 나옵니다.

![tau 조정](../assets/diagram-comp-tau.png)

*`tau`가 작으면 가속도계 잡음이 통과하고 `tau`가 크면 gyro bias가 통과합니다.*

![tau에 따른 오차](../assets/fig-tau-tradeoff.png)

*예시 값은 `b = 0.01 rad/s`, `s = 0.05 rad`, `dt = 0.01 s`입니다. 시뮬레이션이 유도한 곡선 위에 놓이고 최솟값은 0.40 s에 있습니다.*

위 값에서 `tau = 2 s`이면 bias 오차가 `2 * 0.01 = 0.02 rad`로 남고 `tau = 0.05 s`이면 잡음 오차가 0.015 rad입니다.

`tau = 0.40 s`이면 오차가 0.004와 0.0056이고 둘을 합치면 `sqrt(0.004^2 + 0.0056^2) = 0.0068 rad`입니다.

![가만히 놓인 판 하나, 필터 셋](../assets/clip-example.mp4)

*수평한 판 셋을 보세요. `tau`가 작은 왼쪽 판은 잡음 때문에 떨리고 `tau`가 큰 오른쪽 판은 한쪽으로 기웁니다. 가운데 판이 수평에 가장 가깝습니다. 오차는 10배로 그렸습니다.*

## 만들기

```python
def alpha(tau, dt):
    return tau / (tau + dt)

def complementary(gyro, acc, dt, tau, theta0=0.0):
    a, theta, out = alpha(tau, dt), np.full(gyro.shape[1], theta0, float), []
    for g, z in zip(gyro, acc):
        theta = a * (theta + g * dt) + (1 - a) * z
        out.append(theta)
    return np.array(out)
```

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/04-complementary-filter -q
```

## 실제 도구로 보기

`imu_tools`의 `imu_complementary_filter`는 gyro와 가속도계, 선택적으로 자기장 값을 합쳐 orientation quaternion을 냅니다.

필터가 낸 기울기를 이 레슨의 `tau` 트레이드오프와 비교해 보세요.

출처: imu_tools README, https://raw.githubusercontent.com/CCNYRoboticsLab/imu_tools/humble/README.md (2026년 11월 9일 확인).

## 결과물

`outputs/skill-complementary-filter-check.md`는 잰 bias와 잡음에 time constant가 맞는지 검토합니다.

## 연습 문제

1. `tau = 5 s`, `b = 0.01 rad/s`일 때 gyro bias 오차를 계산하고 확인하세요.
2. `s`를 절반으로 줄였을 때 새 최적 `tau`를 예측하세요.
3. 가속도계가 흔들릴 때만 잡음이 크다면 `tau`는 어떻게 해야 할까요?
