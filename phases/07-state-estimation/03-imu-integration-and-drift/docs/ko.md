# IMU 적분과 Drift

> 아주 작은 상수 오차가 있는 센서를 적분하면 그 오차가 직선, 포물선, 3차 곡선으로 자랍니다. 3차로 만드는 통로가 중력입니다.

**유형:** 만들기   **선수 지식:** 07/02 Kalman Filter   **시간:** 약 15분

## 쉽게 말하면

로봇이 가만히 서 있는데 회전 속도를 재는 센서인 gyro가 있지도 않은 작은 회전을 읽어요. 그 값을 계속 더하니 로봇은 자기가 서서히 기울고 있다고 생각해요.

가속도계는 가만히 있어도 gravity를 느끼고 로봇은 자기 기울기 추정으로 gravity를 빼요. 기울기가 틀리면 gravity 일부가 실제로는 없는 옆으로 미는 힘으로 남아요. 이 힘을 더하면 속도가 되고 속도를 더하면 거리가 되어서 로봇은 자기가 굴러간다고 믿어요.

## 문제

가만히 선 로봇의 IMU(gyro와 가속도계가 든 칩)는 회전은 거의 없고 gravity 말고는 미는 힘도 없다고 읽습니다. gyro bias(작고 일정한 오차) 0.01 rad/s와 가속도계 bias 0.05 m/s^2를 줘 보세요.

20초 동안 더하면 로봇이 11도 돌고 10 m 움직인 것으로 나오고 gravity 때문에 더 나빠집니다.

## 개념

![적분할 때마다 drift의 차수가 오릅니다](../assets/diagram-drift-orders.png)

*각 줄을 따라가 보세요. gyro는 한 번 더해 각도를, 가속도계는 두 번 더해 위치를 얻고 더할 때마다 `t`의 제곱이 하나씩 붙습니다.*

적분은 값을 시간에 걸쳐 계속 더하는 일입니다. 일정한 gyro bias `b`는 각도 오차 `b t`를 만듭니다.

일정한 가속도계 bias `a`는 속도 오차 `a t`와 위치 오차 `a t^2 / 2`를 만듭니다.

샘플마다 크기 `sigma`인 백색 잡음을 `dt` 간격으로 받으면 random walk가 더해지고 그 전형적인 크기는 `sigma * sqrt(dt * t)`입니다.

![유도한 식과 겹치는 각도와 위치 오차](../assets/fig-imu-drift.png)

*잡음이 낀 15번의 실행이 유도한 직선 `b t`(각도)와 곡선 `a t^2 / 2`(위치) 주위에서 흔들립니다.*

![gyro bias가 중력을 통해 위치로 새어 나옵니다](../assets/diagram-gravity-leak.png)

*기울기 오차가 있으면 로봇이 중력을 엉뚱한 방향으로 뺍니다. 남은 값이 실제 가속도처럼 보입니다.*

![3차 증가가 2차 증가를 앞지릅니다](../assets/fig-gravity-leak.png)

*3차 곡선(gyro bias)이 2차 곡선(가속도계 bias)을 약 1.5초 뒤에 추월하는 모습을 보세요. 기울기 오차는 `b t`이므로 가짜 가속도는 `g sin(b t)`이고 각도가 작으면 약 `g b t`입니다. 이렇게 커지는 값을 두 번 더하면 `g b t^3 / 6`입니다.*

gyro bias `0.01 rad/s`를 예로 들어 봅시다. 10초 뒤 기울기는 `0.1 rad` 틀리고 gravity는 가짜 가속도 `9.81 * sin(0.1) = 0.98 m/s^2`를 남깁니다.

위치 오차는 약 `9.81 * 0.01 * 10^3 / 6 = 16 m`입니다. 반면 가속도계 bias `0.05 m/s^2`는 `0.05 * 10^2 / 2 = 2.5 m`만 만듭니다.

![가만히 선 로봇이 미끄러진다고 믿는 모습](../assets/clip-example.mp4)

*초록 로봇은 가만히 있고 호박색 복사본을 보세요. 기울기가 커지고 빨간 화살표는 가짜로 미는 힘이며 복사본은 점점 빨리 미끄러집니다. 기울기는 5배로 크게 그렸고 10초를 5초에 재생했으며 1 m를 0.1 m로 그렸습니다.*

## 만들기

```python
meas = omega_true + bias + sigma * rng.standard_normal((n, runs))
angle = np.cumsum(meas, axis=0) * dt

fake_a = G * np.sin(bias_g * t)          # tilt error b*t leaks gravity
pos = np.cumsum(np.cumsum(fake_a) * dt) * dt
```

테스트는 합을 정확한 이산 공식과 유도한 `b t`, `a t^2 / 2`, `g b t^3 / 6`에 비교합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/03-imu-integration-and-drift -q
```

## 실제 도구로 보기

`imu_tools`의 `imu_filter_madgwick`는 gyro와 가속도계, 선택적으로 자기장 값을 합쳐 orientation을 냅니다.

여기서 본 drift를 그 filter가 바로잡아야 합니다. 정지 상태 녹화를 넣고 각도가 더 이상 drift하지 않는지 확인해 보세요.

출처: imu_tools README, https://github.com/CCNYRoboticsLab/imu_tools (2026년 11월 9일 확인).

## 결과물

`outputs/skill-imu-drift-check.md`는 IMU만으로 낸 추정값이 얼마나 오래 쓸 만한지 계산합니다.

## 연습 문제

1. `b = 0.01 rad/s`일 때 각도 오차가 1도에 이르는 시간을 구하세요.
2. `dt`를 두 배로 하면 10초 시점의 각도 오차가 바뀌는지 보세요.
3. 기울기 오차가 5초 시점 값에 머문다면 위치 오차를 식으로 쓰세요.
