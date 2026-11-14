# Encoder와 양자화 (Encoders and Quantisation)

> encoder는 정수 카운트만 알려 주므로 느린 관절의 속도는 들쭉날쭉하고 그것을 진정시키는 필터는 모두 속도 값을 늦게 도착시킵니다.

**유형:** 만들기   **선수 지식:** 04/01 모터와 기어박스, 03/01 샘플링 한계   **시간:** 약 15분

## 쉽게 말하면

홈이 뚫린 원판이 고정된 센서 앞을 천천히 지나가요. 센서는 홈 모서리가 하나 더 지나갔다는 것만 알려 주고 그것이 count 하나예요. 속도를 구하려면 센 count 수를 세는 데 걸린 시간으로 나눠요.

천분의 일 초마다 확인하면 대부분 모서리가 안 보이다가 갑자기 하나가 보여요. 원판이 일정하게 돌아도 속도가 영으로 읽히다가 훨씬 높게 읽혀요. 확인 간격을 늘리면 값은 안정되지만 각 값이 더 오래전 순간을 설명해서 속도 변화를 늦게 따라가요.

## 문제

관절을 부드럽게 만들려고 loop 주기를 올렸더니 저속에서 속도 신호가 오히려 나빠집니다. 속도가 0과 큰 값 사이를 뜁니다.
댐핑 항 `kd * 속도`(속도가 커질수록 세지는 브레이크)는 그 값이 뛸 때마다 관절을 걷어찹니다. 필터를 넣으면 걷어차는 일은 멈춥니다. 하지만 속도가 늦게 도착해서 관절이 진동합니다.

## 개념

축 각도는 부드럽고 카운트는 계단이며 차분(이전 카운트를 빼는 것)은 계단 하나하나를 spike로 바꿉니다.

![축 각도에서 속도까지](../assets/diagram-encoder-pipeline.png)

*부드러운 축, 계단 카운트, 뾰족한 속도입니다.*

카운트 하나는 `2*pi / CPR` rad입니다(CPR은 한 바퀴당 카운트 수). 이것을 샘플 시간 `dt`로 나누면 한 샘플 차분이 보고할 수 있는 0이 아닌 가장 작은 속도 `2*pi / (CPR * dt)`(속도 step)가 됩니다.

`CPR = 4096`이고 `dt = 1 ms`이면 1.53 rad/s입니다. 0.1 rad/s로 도는 관절은 약 15 ms마다 카운트 하나를 만들어서 15번 중 14번은 0으로 읽히고 나머지는 1.53으로 읽힙니다. 그래도 평균은 맞습니다.

![창 길이의 교환](../assets/diagram-window-tradeoff.png)

*창이 길수록 step이 작고 노이즈가 적지만 추정값은 더 오래됩니다.*

`n` 샘플 창(카운트를 `n` 샘플 간격으로 비교하는 것)은 step을 `n`으로 나누고 변하는 신호를 `n*dt/2`만큼 늦춥니다. 추정값이 창의 가운데 시점을 설명하기 때문입니다.

이 레슨의 지연 테스트에서는 속도가 2 rad/s^2로 오르고 1 kHz(`dt` = 1 ms)에서 `n = 20`입니다. 추정값은 10 ms 전의 값이므로 `2 * 0.01 = 0.02` rad/s만큼 낮게 읽힙니다.

![속도가 오르는 축을 읽는 속도계 두 개](../assets/clip-example.mp4)

*아주 촘촘한 encoder라서 지연만 남습니다. 파란 바늘(한 샘플)은 참 속도에 붙어 있고 초록 바늘(20 샘플)은 10 ms 늦게 따라옵니다.*

![속도 노이즈와 창에 따른 지연](../assets/fig-encoder-velocity.png)

*왼쪽은 1 kHz에서 드문 높은 spike, 100 Hz에서 작은 계단입니다. 오른쪽은 창이 길수록 노이즈가 줄고 지연은 직선으로 늘어납니다.*

## 만들기

```python
def min_velocity_step(cpr, dt):
    return TWO_PI / cpr / dt

def window_velocity(c, cpr, dt, n):
    return (c[n:] - c[:-n]) * TWO_PI / cpr / (n * dt)

def window_lag(n, dt):
    return n * dt / 2
```

테스트는 출력이 step의 정수배인지, bias가 없는지, 노이즈가 `step * sqrt(d * (1 - d))`와 맞는지(`d`는 카운트가 보이는 읽기의 비율), 지연이 `n*dt/2`인지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/03-encoders-and-quantisation -q
python3 phases/04-actuators-and-sensors/03-encoders-and-quantisation/code/figure.py
```

## 실제 도구로 보기

drive는 창 안의 edge를 세거나 edge 사이 간격을 재서 속도를 추정하며 maxon 문서는 edge를 세는 방식이 아주 낮은 속도에서 어렵다고 설명합니다. 같은 ramp에서 여기의 고정 창 결과와 주기 기반 추정을 비교해 보세요.

출처 (2026년 11월 9일 접속):

- [maxon, encoder selection part three](https://www.maxongroup.com/en-us/knowledge-and-support/blog/encoder-selection-part-three-speed-control-25728)

## 결과물

`outputs/skill-encoder-velocity-check.md`는 속도 step을 계산하고 관절에 맞는 창 길이를 고릅니다.

## 연습 문제

1. 카운트 사이 간격을 재는 주기 기반 추정을 더하고 0.1 rad/s에서 노이즈를 비교하세요.
2. 한 샘플 차분의 오차가 10% 아래로 내려가는 속도를 구하세요.
3. ramp 속도를 바꾸면 `n = 15` 근처의 꺼짐이 움직이는 것을 보이세요.
