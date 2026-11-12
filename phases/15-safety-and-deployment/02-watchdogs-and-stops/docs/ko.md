# Watchdog과 정지 (Watchdogs and Stops)

> watchdog은 timeout이 끝난 뒤 남은 거리 안에서 관절이 멈출 수 있어야 안전합니다.

**유형:** 만들기   **선수 지식:** 15/01 고장 유형   **시간:** 약 15분

## 쉽게 말하면

자전거를 타며 정지 신호를 기다리는 동안에도 앞으로 가요. 브레이크를 잡은 뒤에도 멈출 거리가 필요해요. 페달만 멈추면 그대로 굴러가요.

watchdog도 heartbeat가 끊겼는지 기다린 뒤 정지를 시작해요. timeout 동안 간 거리와 제동 거리가 모두 관절 한계까지 남은 범위 안에 들어가야 해요. 제동 거리는 속도의 제곱에 따라 늘어서 빠를수록 여유가 급히 줄어요.
timeout은 정상 메시지가 조금 늦는 경우도 허용해야 해요.

## 문제

명령을 보내던 프로그램이 죽었는데 관절은 마지막으로 받은 속도를 계속 실행합니다. watchdog이 침묵을 알아채고 관절을 멈춥니다. 그런데 정지에는 시간과 거리가 듭니다. 어떤 정지는 사실 정지가 아닙니다.

## 개념

![heartbeat가 관절의 움직임을 허락합니다](../assets/diagram-watchdog-flow.png)

*명령 source는 명령과 heartbeat를 보냅니다. heartbeat가 timeout보다 길게 끊기면 watchdog이 관절을 정지 동작에 넘깁니다.*

속도 `v`에서 일정한 감속 `a`로 제동하면 `t = v / a`가 걸리고 이동 거리는 `v * t - a * t^2 / 2 = v^2 / (2a)`입니다. 제동이 시작되기 전에도 관절은 timeout `T` 내내 움직입니다.

![source가 죽은 뒤의 거리 예산](../assets/diagram-stop-budget.png)

*timeout 동안의 이동과 제동 이동이 한계까지 남은 거리 안에 들어와야 합니다. 이것이 T의 상한입니다.*

![토크 차단과 ramp 정지의 비교](../assets/fig-cut-vs-ramp.png)

*두 정지는 같은 순간에 시작합니다. 토크를 끊으면 마찰만 남아 관절이 한계를 지나 미끄러집니다. ramp 정지는 한계 훨씬 앞에서 멈춥니다.*

![watchdog timeout에 따른 초과 이동](../assets/fig-timeout-budget.png)

*timeout이 10 ms 늘 때마다 2 rad/s * 10 ms = 0.02 rad가 더해집니다. 식이 보수적인 상한이라 시뮬레이션은 식 바로 아래에 놓입니다.*

timeout에는 하한도 있습니다. heartbeat 주기에 jitter를 더한 값보다 커야 합니다. 그렇지 않으면 늦은 메시지 하나에 관절이 이유 없이 멈춥니다.

## 만들기

```python
def stop_distance(v, a):
    return v * v / (2.0 * a)

def max_timeout(room, v, a):
    return (room - stop_distance(v, a)) / v   # raises if this is <= 0
```

`simulate()`는 2 rad/s로 움직이는 관절과 1.5 rad 한계를 두고 0.5초에 source를 죽입니다. 그다음 `"cut"`(토크 0)이나 `"ramp"`(8 rad/s^2 제동)를 적용합니다.

테스트는 마찰 없는 실행과 식을 비교하고 미끄러지는 거리 `J v / b`와 timeout 상한을 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/02-watchdogs-and-stops -q
python3 phases/15-safety-and-deployment/02-watchdogs-and-stops/code/main.py
```

## 실제 도구로 보기

실제 drive에는 brake와 최대 안전 감속과 자체 timeout이 있습니다. 값은 drive 문서에서 읽어 `max_timeout`에 넣습니다. 이 관절은 brake를 모델링하지 않으므로 cut 결과는 drive의 도움이 없는 경우로 읽습니다.

## 결과물

`outputs/skill-watchdog-budget.md`는 watchdog timeout을 정지 거리 예산과 heartbeat 주기에 맞춰 점검합니다.

## 연습 문제

1. 속도를 4 rad/s로 두 배 올리고 같은 0.5 rad 여유로는 `max_timeout`이 더 이상 성립하지 않음을 보이세요.
2. `max_timeout`이 예외를 낼 때까지 감속을 낮추고 설계에 어떤 뜻인지 설명하세요.
3. heartbeat에 5 ms jitter를 더하고 오탐 없는 가장 짧은 timeout을 찾으세요.
