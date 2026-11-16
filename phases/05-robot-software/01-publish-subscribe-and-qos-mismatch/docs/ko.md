# Publish-Subscribe와 QoS 불일치

> 두 ROS 프로그램이 둘 다 잘 돌아가는데도 메시지를 전혀 주고받지 못하는 이유를 배웁니다.

**유형:** 만들기   **선수 지식:** 00/04 한 페이지로 보는 ROS 2   **시간:** 약 15분

## 쉽게 말하면

로버가 메시지로 자기 위치를 로봇 팔에 알려 줘요. 연결하기 전에 양쪽은 각자 전달 약속을 밝혀요. 이 약속을 QoS(quality of service)라고 불러요.

로버는 보내 보겠다고만 약속하는데 팔은 반드시 전달되는 방식만 받겠다고 해요. 그러면 둘은 연결되지 않고 아무도 불평하지 않으며 팔은 가만히 있어요.

## 핵심 용어

- **Node**: 로봇 소프트웨어 틀인 ROS 2에서 실행 중인 프로그램입니다.
- **Topic**: node들이 메시지를 보내고 받는 이름 붙은 통로입니다.
- **Publisher / Subscriber**: topic에서 보내는 쪽과 듣는 쪽입니다.
- **QoS**: quality of service로 연결하기 전에 양쪽이 밝히는 전달 약속입니다.
- **Callback**: 메시지가 도착할 때마다 그것을 처리하는 함수입니다.
- **Queue depth**: 읽지 않은 메시지가 몇 개까지 기다릴 수 있는지입니다. 넘으면 가장 오래된 것을 버립니다.

## 문제

로버가 자기 위치를 보내고 팔이 듣고 있는데 팔이 전혀 움직이지 않고 죽은 것도 없습니다. 둘이 서로 다른 전달 보장을 요구해서 ROS가 둘을 연결하지 않았기 때문입니다.

## 개념

로봇은 메시지를 주고받는 여러 프로그램이고 이 조용한 불일치는 죽은 센서와 똑같아 보입니다.

![요구와 제공](../assets/diagram-qos-match.png)

*로버는 best effort를 제공하고 팔은 reliable을 요구하므로 맞지 않습니다.*

양쪽은 각자 QoS profile을 선언합니다. Reliability에서 best effort는 한 번 보내고 넘어가고 reliable은 잃어버린 메시지를 다시 보냅니다.
Durability에서 volatile은 늦게 온 subscriber에게 아무것도 주지 않고 transient local은 지난 메시지를 줍니다. subscriber가 publisher의 제공보다 더 많이 요구하지 않을 때만 연결됩니다.
reliable publisher에 best effort subscriber는 괜찮고 반대는 안 됩니다.

![깊이가 있는 queue](../assets/diagram-qos-queue.png)

*keep-last queue는 최신 N개를 담고 가장 오래된 것을 버립니다.*

연결된 쌍도 callback이 publisher보다 느리면 메시지를 잃습니다. 로버가 메시지 8개를 한꺼번에 보내고 팔이 tick(시뮬레이션 한 스텝)마다 하나씩 처리한다고 합시다. depth 1이면 `run()`은 1개를 전달하고 7개를 버립니다.
depth 8이면 8개를 모두 전달합니다.

![메시지 8개와 팔 두 개](../assets/clip-example.mp4)

*같은 묶음입니다. 파랑은 칸이 하나여서 메시지 일곱 개가 떨어집니다. 초록은 칸이 여덟 개여서 팔이 모두 따라갑니다.*

![전달과 손실](../assets/fig-qos-delivery.png)

*왼쪽은 불일치한 쌍이 0%를 전달하는 모습입니다. 오른쪽은 8개 묶음에 depth 8이 필요하고 계속되는 과부하는 depth와 상관없이 절반을 버리는 모습입니다.*

## 만들기

```python
def compatible(pub, sub):
    if pub.reliability == "best_effort" and sub.reliability == "reliable":
        return False, "reliability: ..."
    if pub.durability == "volatile" and sub.durability == "transient_local":
        return False, "durability: ..."
    return True, "ok"
```

`Queue.push()`는 항목을 더하고 `depth`를 넘으면 가장 오래된 것을 빼며 버린 수를 셉니다.
`run()`은 tick마다 `arrivals[t]`개의 메시지를 publish하고 best effort 링크에서는 일부를 잃으며 callback이 tick마다 하나씩 가져가게 합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/01-publish-subscribe-and-qos-mismatch -q
```

## 실제 도구로 보기

`compatible()`을 ROS 2 QoS 문서의 표와 비교해 보세요.

출처: ROS 2 Jazzy, "Quality of Service settings" (https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html), 2026년 11월 9일 확인.

## 결과물

`outputs/skill-qos-mismatch-check.md`는 조용한 topic을 profile, 호환성, queue 점검 순서로 따라가며 확인합니다.

## 연습 문제

1. subscriber의 deadline이 publisher의 것보다 짧으면 거부하는 deadline 정책을 더하세요.
2. `Queue`에 keep-all 모드를 주고 과부하에서 메모리가 어떻게 늘어나는지 보이세요.
3. transient-local publisher가 늦게 온 subscriber에게 마지막 `depth`개의 메시지를 다시 보내게 하세요.
