# 차동 구동과 Odometry (Differential Drive and Odometry)

> 바퀴 속도로 자세를 얻으려면 길이 두 개를 정확히 알아야 합니다. 추정값은 그 값이 틀렸다는 사실을 알려 주지 못합니다.

**유형:** 만들기   **선수 지식:** 01/01 회전과 SE(3)   **시간:** 약 15분

## 문제

모바일 로봇을 한 변이 2 m인 사각형으로 몰았더니 바퀴 odometry는 출발점으로 돌아왔다고 합니다. 줄자로 재면 출발점에서 18 cm 떨어져 서 있습니다. 바퀴는 명령대로 돌았으므로 모터 문제가 아닙니다. 설정 파일에 넣은 숫자 두 개가 틀린 것입니다.

## 개념

![바퀴 속도에서 자세까지](../assets/diagram-wheels-to-pose.png)

*바퀴 속도 두 개가 전진 속도와 회전율이 됩니다. 이것을 시간에 따라 더하면 자세가 됩니다.*

전진 속도는 두 바퀴 가장자리 속도의 평균인 `v = r (wr + wl) / 2`입니다. 회전율은 속도 차를 윤거로 나눈 `w = r (wr - wl) / b`입니다.

dead reckoning은 매 step마다 `v dt`와 `w dt`를 더합니다. 이 레슨은 각 step을 정확한 원호로 적분합니다.

![작은 오차 두 개, 서로 다른 피해](../assets/diagram-two-errors.png)

*추정값은 계획과 같은 틀린 `r`과 `b`를 쓰므로 루프를 닫아 버리고 문제의 징후를 전혀 보이지 않습니다.*

![사각형 하나의 실제 경로와 odometry 경로](../assets/fig-odometry-drift.png)

*왼쪽은 윤거가 2% 크면 실제 로봇이 출발점에서 0.18 m 떨어지는 모습입니다. 오른쪽은 간격이 선형으로 커지는 모습입니다. 같은 크기의 반지름 오차도 거의 같은 피해를 줍니다.*

모서리마다 틀린 각도로 돌아서 네 변의 합이 더는 0이 되지 않습니다. 회전 오차를 `k`라 하면 간격은 `a = (pi/2) / k`일 때 `L |1 + e^(ia) + e^(2ia) + e^(3ia)|`이고 테스트가 이를 확인합니다.

## 만들기

```python
def wheels_to_twist(wl, wr, r, b):
    return r * (wr + wl) / 2, r * (wr - wl) / b

def dead_reckon(wl, wr, dt, r, b, pose0=(0.0, 0.0, 0.0)):
    v, w = wheels_to_twist(np.asarray(wl, float), np.asarray(wr, float), r, b)
    dth = w * dt
    step = v * dt * np.sinc(dth / (2 * np.pi))  # chord of the arc
    th = pose0[2] + np.cumsum(dth) - dth / 2
```

`square_wheels()`는 기준값 `r`과 `b`로 사각형을 계획합니다. `closure_error()`는 같은 바퀴 명령을 다른 `r`과 `b`로 다시 재생합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/01-differential-drive-and-odometry -q
python3 phases/08-mobile-robots/01-differential-drive-and-odometry/code/main.py
```

## 실제 도구로 보기

ROS 2의 diff_drive_controller는 `wheel_separation`과 `wheel_radius`를 요구합니다. 문서는 separation이 틀리면 커브에서 로봇이 이상하게 움직인다고 경고합니다. radius가 틀리면 기대보다 빠르거나 느리게 움직인다고도 합니다.

보정 계수인 `wheel_separation_multiplier`도 있습니다. 길이를 잰 사각형을 달리고 간격이 닫힐 때까지 조정해서 보정합니다.

출처: control.ros.org, diff_drive_controller 사용자 문서(jazzy), 2026년 11월 9일에 열어 확인했습니다.

## 결과물

`outputs/skill-odometry-calibration-check.md`는 잰 루프 간격을 의심되는 파라미터와 보정 주행으로 바꿔 줍니다.

## 연습 문제

1. 두 바퀴의 반지름을 다르게 주고 직선이 휘는 것을 보이세요.
2. 사각형을 시계 방향으로 달리고 간격 벡터가 반시계 방향으로 달렸을 때의 간격 벡터와 거울상임을 보이세요.
3. 회전할 때 바퀴가 1% 미끄러지게 하고 어느 오차처럼 보이는지 찾으세요.
