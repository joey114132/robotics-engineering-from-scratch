# Watchdog과 정지 (Watchdogs and Stops)

> 제어 프로그램이 죽었을 때 로봇이 안전하게 멈추게 하는 법을 배웁니다.

**유형:** 만들기   **선수 지식:** 15/01 고장 유형   **시간:** 약 15분

## 쉽게 말하면

watchdog은 작업대 위 로봇 팔을 조종하는 프로그램이 규칙적으로 보내는 "아직 살아 있다"는 신호를 듣고 있어요. 신호가 너무 오래 끊기면 정지를 명령해요. 그 기다림이 timeout이에요.

팔은 그 timeout 동안에도 계속 움직이고 제동에도 거리가 들어요. 전원을 끊는 것은 제동이 아니에요. 자전거 페달을 멈춰도 계속 굴러가듯 팔도 계속 굴러가요.

## 핵심 용어

- **Watchdog**: 기다리던 메시지가 끊기면 정지를 명령하는 monitor입니다.
- **Heartbeat**: 관절에 명령을 보내는 프로그램이 규칙적으로 보내는 "아직 살아 있다"는 메시지입니다.
- **Timeout `T`**: watchdog이 작동하기 전까지 조용한 시간을 참아 주는 길이입니다.
- **Deceleration `a`**: 제동하는 동안 속도가 줄어드는 빠르기입니다.
- **Hard stop**: 관절의 움직임 끝을 막는 블록입니다.
- **Timing jitter**: 메시지 도착 시각이 흔들리는 정도입니다.

## 문제

팔이 움직이는 중에 제어 프로그램이 죽었는데 팔은 마지막 속도로 계속 갑니다. watchdog이 알아채지만 멈추는 데도 시간과 거리가 들어서 팔이 먼저 hard stop에 닿을 수 있습니다.

## 개념

소프트웨어는 죽기도 하므로 실제 로봇은 소프트웨어가 조용해지면 스스로 멈출 수 있어야 합니다. 팔은 timeout 동안 계속 움직이고 그다음 제동에 거리가 더 듭니다. 둘을 합친 거리가 hard stop까지 남은 거리 안에 들어와야 합니다.
timeout이 길면 위험하고 너무 짧으면 팔이 이유 없이 멈춥니다.

![watchdog 흐름](../assets/diagram-watchdog-flow.png)

*heartbeat가 timeout보다 길게 끊기면 정지를 작동시킵니다.*

![정지 거리 예산](../assets/diagram-stop-budget.png)

*timeout 동안의 이동과 제동 이동이 남은 거리 안에 들어와야 합니다.*

![timeout 두 가지](../assets/clip-example.mp4)

*초록 팔은 금방 작동해 stop 앞에서 멈춥니다. 파란 팔은 너무 오래 기다리다 stop에 부딪힙니다.*

![차단과 ramp 비교](../assets/fig-cut-vs-ramp.png)

*모터를 끄면 관절이 한계를 지나 굴러갑니다. 일정한 제동은 한계 앞에서 멈춥니다.*

![timeout 예산](../assets/fig-timeout-budget.png)

*timeout이 길수록 팔이 한계를 더 멀리 지나서 끝나고 그 거리가 고르게 늘어납니다.*

<details><summary>The math (optional)</summary>

속도 `v`에서 일정한 감속 `a`로 제동하면 이동 거리는 `v^2 / (2a)`입니다. timeout은 `v T + v^2 / (2a) <= room`을 만족해야 하므로 `max_timeout = (room - v^2/(2a)) / v`입니다.
예를 들어 관절은 1.0 rad에서 2 rad/s로 움직이고 stop은 1.5 rad에 있으므로 여유는 0.5 rad입니다.
8 rad/s^2로 제동하면 2^2 / (2 * 8) = 0.25 rad가 필요하고 timeout에 쓸 거리는 0.25 rad가 남으므로 T <= 0.25 / 2 = 0.125초입니다.
timeout 0.05초는 시뮬레이션에서 1.30 rad에 멈춥니다. timeout 0.2초는 제동을 시작하기 전에 0.4 rad를 가고 stop에 부딪힙니다. timeout이 10 ms 늘 때마다 0.02 rad가 더해집니다.
timeout은 heartbeat 주기에 jitter를 더한 값보다도 커야 합니다. 그렇지 않으면 늦은 메시지 하나에 관절이 멈춥니다.

</details>

## 만들기

`stop_distance`는 제동 거리를 주고 `max_timeout`은 남은 거리에 맞는 가장 긴 timeout을 줍니다.

```python
def stop_distance(v, a):
    return v * v / (2.0 * a)

def max_timeout(room, v, a):
    return (room - stop_distance(v, a)) / v   # raises if this is <= 0
```

`simulate()`는 0.5초에 명령 프로그램을 죽인 뒤 모터를 끄거나(`"cut"`) 일정하게 제동합니다(`"ramp"`).

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/15-safety-and-deployment/02-watchdogs-and-stops -q
python3 phases/15-safety-and-deployment/02-watchdogs-and-stops/code/main.py
```

## 실제 도구로 보기

실제 drive의 문서에 적힌 brake 값을 `max_timeout`에 넣습니다.

## 결과물

`outputs/skill-watchdog-budget.md`는 timeout을 정지 거리 예산과 heartbeat 주기에 맞춰 점검합니다.

## 연습 문제

1. 속도를 두 배로 올리세요. 같은 여유로 여전히 되나요?
2. `max_timeout`이 예외를 낼 때까지 제동을 낮추세요. 무슨 뜻인가요?
3. heartbeat jitter를 더하세요. 어떤 timeout이면 오탐 정지가 없나요?
