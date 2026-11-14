# Executor와 Callback

> 스레드 하나는 callback 하나씩만 실행하므로 느린 callback 하나가 주기와 상관없이 다른 모든 callback을 기다리게 합니다.

**유형:** 만들기   **선수 지식:** 05/01 Publish-Subscribe와 QoS 불일치   **시간:** 약 15분

## 쉽게 말하면

장난감 자동차는 heartbeat timer가 계속 울리는 동안에만 달려요. 울림이 늦으면 heartbeat를 지켜보는 감시자인 watchdog이 차를 세워요. 차의 프로그램에는 일꾼이 하나뿐이고 이 일꾼을 스레드(thread)라고 불러요.
일꾼은 한 번에 한 가지 일만 해요.
일꾼이 긴 이미지 작업에 매달려 있으면 heartbeat는 줄을 서서 기다리고 차는 멈춰요.

일꾼이 한 명 더 있으면 그동안 heartbeat를 맡을 수 있어요. 다만 두 작업이 같은 데이터를 고치듯 겹치면 안 된다는 규칙이 있으면 그럴 수 없어요. callback group이 이 규칙을 담고 있어요.

## 문제

한 node에 heartbeat를 보내려고 1초에 100번 울리는 timer가 있습니다. 메시지마다 ROS 2가 실행하는 함수인 callback이 이미지 처리에 60 ms를 쓰는 subscription도 있습니다.
heartbeat가 끊기고 다른 곳의 watchdog이 이 node가 죽었다고 판단합니다. callback은 하나하나 모두 맞게 짜여 있고 CPU도 대부분 놀고 있습니다.

## 개념

![스레드 하나와 느린 callback 하나](../assets/diagram-executor-starve.png)

*두 callback이 하나뿐인 스레드를 필요로 하므로 timer는 느린 callback이 끝날 때까지 기다립니다.*

executor는 준비된 callback 중 무엇을 어느 스레드에서 실행할지 정합니다. callback은 group으로 묶입니다.
mutually exclusive group은 자기 callback 둘을 동시에 실행하지 않아서 둘이 함께 쓰는 데이터를 지킵니다. 서로 다른 group의 callback은 병렬로 실행될 수 있습니다.

![스레드와 group](../assets/diagram-callback-groups.png)

*각 줄을 왼쪽에서 오른쪽으로 읽어 보세요. 두 callback이 서로 다른 group에 있을 때만 두 번째 스레드가 도움이 됩니다.*

예를 들어 느린 callback이 0 ms에 시작해서 스레드를 60 ms 동안 쥔다고 해 보겠습니다.
timer는 1 ms에 준비되므로 스레드가 하나이거나 스레드 둘에 group이 하나뿐이면 59 ms를 기다리고 이것이 `simulate()`가 보고하는 최악 대기입니다.
group이 따로면 두 번째 스레드가 timer를 바로 시작하므로 대기는 0입니다.

![스레드가 두 개씩인 자동차 두 대](../assets/clip-example.mp4)

*지붕의 램프 하나가 스레드 하나이고 일하는 동안 켜집니다. 파란 차는 group 하나를 공유해서 두 번째 램프가 꺼져 있고 차는 계속 멈춥니다. 초록 차는 group이 따로라서 두 램프가 모두 일하고 멈추지 않습니다.*

![두 구성의 시간선](../assets/fig-executor-timeline.png)

*스레드 하나에서는 timer가 최대 59 ms 늦게 시작합니다. 스레드 둘에 group을 나누면 기다리지 않습니다.*

## 만들기

```python
busy = {g for _, g in running if g is not None}
job = next((j for j in pending if j[3] is None or j[3] not in busy), None)
```

`simulate()`는 시간을 1 ms씩 진행합니다. 매 단계마다 주기적 callback을 준비 상태로 만들고 끝난 job을 비웁니다. 그다음 놀고 있는 스레드마다 group이 쉬고 있는 가장 오래된 job을 줍니다.

`latencies()`는 준비된 시점과 시작 시점의 차이를 돌려줍니다.

이 모델은 먼저 온 것부터 처리하는 FIFO이고 놓친 tick을 전부 쌓아 둡니다. 문서에는 과부하 상태의 executor가 준비된 일을 돌아가며 처리하는 round-robin 방식이라고 되어 있습니다.
숫자를 비교하기 전에 문서의 "Scheduling semantics" 절을 읽으세요.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/02-executors-and-callbacks -q
python3 phases/05-robot-software/02-executors-and-callbacks/code/main.py
```

## 실제 도구로 보기

ROS 2에도 같은 부품이 있습니다. 단일 스레드 executor, 멀티 스레드 executor, mutually exclusive와 reentrant(자기 group 동료와 겹쳐 실행될 수 있음) callback group입니다.

group 없이 만든 callback은 node의 default group에 들어갑니다. 그래서 데이터를 공유하지 않는다면 스레드를 늘리기 전에 느린 callback에 자기 group부터 주세요.

출처: ROS 2 Jazzy, "Executors".
https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Executors.html

2026년 11월 9일에 ros2/ros2_documentation의 `jazzy` branch 소스 파일에서 읽었습니다.

## 결과물

`outputs/skill-executor-starvation-check.md`는 다른 callback을 굶기는 callback을 찾아 어떤 수정이 맞는지 알려 줍니다.

## 연습 문제

1. reentrant group(`None`)에 느린 job 둘을 넣고 스레드 둘에서 겹쳐 실행되는 것을 보이세요.
2. timer가 놓친 tick을 쌓지 않고 버리게 한 뒤 최악 대기 시간을 비교하세요.
3. 느린 callback을 10 ms 조각 여섯 개로 나누고 스레드 하나에서 timer의 최악 대기 시간을 보고하세요.
