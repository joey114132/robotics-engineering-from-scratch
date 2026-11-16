# Encoder와 양자화 (Encoders and Quantisation)

> 느리게 도는 관절의 속도 값이 왜 들쭉날쭉한지, 그리고 그것을 부드럽게 하면 왜 늦어지는지 배웁니다.

**유형:** 만들기   **선수 지식:** 04/01 모터와 기어박스, 03/01 샘플링 한계   **시간:** 약 15분

## 쉽게 말하면

홈이 뚫린 원판이 고정된 센서 앞을 천천히 지나가요. 센서는 홈 모서리가 하나 더 지나갔다는 것만 알려 주고 그것이 count 하나예요. 속도는 센 count 수를 센 시간으로 나눈 값이에요.

자주 확인하면 대부분 아무것도 안 보이다가 갑자기 모서리 하나가 보여서 속도가 튀어요. 오래 기다리면 안정되지만 각 값이 더 오래된 순간을 말해요.

## 핵심 용어

- **Encoder**: 축이 얼마나 돌았는지 정수 단계로 알려 주는 센서입니다.
- **Count**: encoder가 알려 주는 한 단계입니다. 여기서는 홈 모서리 하나가 센서를 지나간 것입니다.
- **CPR**: 한 바퀴당 count 수입니다. 한 바퀴가 몇 단계인지 알려 줍니다.
- **Quantisation**: 부드러운 값을 정수 단계로 반올림하는 일입니다. 작은 변화는 보이지 않게 됩니다.
- **Window**: 속도를 구하려고 견주는 두 count 사이의 샘플 수입니다.
- **Damping term**: `kd * velocity`로 속도가 클수록 세지는 브레이크입니다.

## 문제

관절이 느리고 매끄럽게 도는데도 속도 값이 0과 큰 값 사이를 뛰고 damping 항이 그때마다 관절을 걷어찹니다. 필터를 넣으면 걷어차는 일은 멈춥니다. 하지만 속도가 늦게 도착해서 관절이 진동합니다.

## 개념

관절의 속도는 보통 encoder count에서 구하므로 느리게 움직이는 로봇은 모두 이 문제를 만납니다.

카운트는 계단이고 차분(이전 카운트를 빼는 것)은 계단 하나하나를 spike로 바꿉니다.

![각도에서 속도까지](../assets/diagram-encoder-pipeline.png)

*부드러운 축, 계단 카운트, 뾰족한 속도입니다.*

카운트 하나는 `2*pi / CPR` rad입니다. 이것을 샘플 시간 `dt`로 나누면 한 샘플 차분이 보고할 수 있는 0이 아닌 가장 작은 속도 `2*pi / (CPR * dt)`가 됩니다. `CPR = 4096`이고 `dt = 1 ms`이면 1.53 rad/s입니다.
0.1 rad/s로 도는 관절은 약 15 ms마다 카운트 하나를 만들어서 15번 중 14번은 0으로 읽히고 나머지는 1.53으로 읽힙니다.

![창 길이의 교환](../assets/diagram-window-tradeoff.png)

*창이 길수록 step이 작고 노이즈가 적지만 추정값은 더 오래됩니다.*

`n` 샘플 창은 step을 `n`으로 나누고 변하는 신호를 `n*dt/2`만큼 늦춥니다. 이 레슨의 지연 테스트에서는 속도가 2 rad/s^2로 오르고 `n = 20`, `dt = 1 ms`입니다.
추정값은 10 ms 전의 값이므로 `2 * 0.01 = 0.02` rad/s만큼 낮게 읽힙니다.

![속도계 두 개](../assets/clip-example.mp4)

*파란 바늘(한 샘플)은 참 속도에 붙어 있고 초록 바늘(20 샘플)은 10 ms 늦게 따라옵니다.*

![노이즈와 지연](../assets/fig-encoder-velocity.png)

*왼쪽은 1 kHz에서 드문 높은 spike, 100 Hz에서 작은 계단입니다. 오른쪽은 창이 길수록 노이즈가 줄고 지연이 늘어납니다.*

## 만들기

```python
def min_velocity_step(cpr, dt):
    return TWO_PI / cpr / dt

def window_velocity(c, cpr, dt, n):
    return (c[n:] - c[:-n]) * TWO_PI / cpr / (n * dt)

def window_lag(n, dt):
    return n * dt / 2
```

테스트는 출력이 step의 정수배인지, bias가 없는지, 노이즈 크기와 지연 `n*dt/2`가 맞는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/03-encoders-and-quantisation -q
python3 phases/04-actuators-and-sensors/03-encoders-and-quantisation/code/figure.py
```

## 실제 도구로 보기

drive는 창 안의 edge를 세거나 edge 사이 간격을 재서 속도를 추정합니다.

출처 (2026년 11월 9일 접속):

- [maxon, encoder selection part three](https://www.maxongroup.com/en-us/knowledge-and-support/blog/encoder-selection-part-three-speed-control-25728)

## 결과물

`outputs/skill-encoder-velocity-check.md`는 속도 step을 계산하고 관절에 맞는 창 길이를 고릅니다.

## 연습 문제

1. 카운트 사이 간격을 재서 0.1 rad/s에서 노이즈를 비교하세요.
2. 한 샘플 차분의 오차가 10% 아래로 내려가는 속도를 구하세요.
3. ramp 속도를 바꾸면 `n = 15` 근처의 꺼짐이 움직이는 것을 보이세요.
