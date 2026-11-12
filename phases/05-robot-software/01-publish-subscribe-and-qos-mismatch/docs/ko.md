# Publish-Subscribe와 QoS 불일치

> subscriber는 publisher가 제공하는 것보다 더 많이 요구할 수 없습니다. 요구하면 아무것도 전달되지 않고 아무 경고도 없습니다.

**유형:** 만들기   **선수 지식:** 00/04 한 페이지로 보는 ROS 2   **시간:** 약 15분

## 쉽게 말하면

학급에 노트를 전달하려는데 자원한 친구는 최대한 해 보겠다고 해요. 선생님이 반드시 전달을 보장하는 방식만 받겠다고 하면 아예 시작에 합의하지 못해요. 전달하다 가끔 노트를 잃는 경우와는 달라요.

QoS도 reliable을 요구하는 subscriber와 best effort publisher는 연결되지 않아 아무것도 오지 않아요. 반대로 reliable을 제공하면 그보다 적게 요구하는
subscriber도 받을 수 있어요. 연결된 뒤에도 callback이 느려 queue가 넘치면 메시지는 버려질 수 있어요.

## 문제

카메라 driver는 이미지를 publish하고 viewer는 subscribe하는데 viewer 화면이 비어 있습니다. 양쪽 모두 존재하고 node도 죽지 않았으며 에러도 나오지 않습니다. 두 쪽이 서로 다른 전달 보장을 요구해서 middleware가 둘을 연결하지 않은 것입니다.

## 개념

![요청과 제공의 비교](../assets/diagram-qos-match.png)

*best effort publisher는 reliable subscriber를 만족시킬 수 없어서 이 쌍은 연결되지 않습니다.*

양쪽은 각자 QoS profile을 선언합니다. reliability, durability, history depth가 그 내용입니다.

subscriber가 모든 policy에서 publisher가 제공하는 것 이하만 요구해야 쌍이 연결됩니다. reliable publisher와 best effort subscriber는 괜찮고 반대는 안 됩니다.

![depth가 있는 큐](../assets/diagram-qos-queue.png)

*keep-last 큐는 메시지 N개를 담고 새 메시지가 오면 가장 오래된 것을 버립니다.*

연결된 쌍도 callback이 publisher보다 느리면 메시지를 잃습니다(이 bus는 레슨 00/04에서 만들었습니다). 여기서는 depth를 burst와 과부하에 대해 시험합니다.

![전달과 유실](../assets/fig-qos-delivery.png)

*왼쪽은 불일치 쌍만 0%를 전달하는 모습입니다. 오른쪽은 8개짜리 burst에 depth 8이 필요하고 지속적인 과부하는 어떤 depth에서도 약 절반을 버리는 모습입니다.*

## 만들기

```python
def compatible(pub, sub):
    if pub.reliability == "best_effort" and sub.reliability == "reliable":
        return False, "reliability: ..."
    if pub.durability == "volatile" and sub.durability == "transient_local":
        return False, "durability: ..."
    return True, "ok"
```

`Queue.push()`는 메시지를 넣고 `depth`를 넘으면 가장 오래된 것을 빼며 유실을 셉니다. `run()`은 tick마다 `arrivals[t]`개를 publish하고 best effort 링크에서 일부를 잃으며 callback이 tick당 하나씩 가져가게 합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/01-publish-subscribe-and-qos-mismatch -q
```

## 실제 도구로 보기

`compatible()`을 ROS 2 QoS 문서의 표와 비교해 보세요. publisher와 subscription이 보고할 수 있는 incompatible-QoS 이벤트도 같이 보세요.

문서에 적힌 기본값은 keep last, depth 10, reliable, volatile입니다.

출처: ROS 2 Jazzy, "Quality of Service settings".
https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html

2026년 11월 9일에 ros2/ros2_documentation의 `jazzy` branch 소스 파일에서 읽었습니다.

## 결과물

`outputs/skill-qos-mismatch-check.md`는 조용한 topic을 profile, 호환성, 큐 순서로 점검합니다.

## 연습 문제

1. deadline policy를 추가하고 publisher보다 짧은 subscriber deadline을 거부하는 규칙을 넣으세요.
2. `Queue`에 keep-all 모드를 넣고 지속적인 과부하에서 필요한 메모리를 보이세요.
3. transient-local publisher가 늦게 온 subscriber에게 마지막 `depth`개를 다시 보내게 하세요.
