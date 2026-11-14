# ROS 2 한 장 요약

> node는 topic과 service로 데이터를 주고받고 queue depth가 느린 subscriber의 손실을 정합니다.

**유형:** 배우기   **선수 지식:** 00/01 Python 환경과 numpy   **시간:** 약 15분

## 쉽게 말하면

컵이 레일 위를 미끄러져요. 센서는 컵의 위치를 팔의 controller가 읽는 것보다 빠르게 알려 줘요.
읽지 못한 보고는 queue에서 기다리고 controller는 언제나 가장 오래된 보고부터 가져가요.

queue가 가득 차면 새 보고가 올 때마다 가장 오래된 보고가 밀려나요.
queue가 길면 기다리는 가장 오래된 보고가 반 초 전 것일 수도 있어서 팔은 컵이 있던 자리를 향해요. 보고를 하나만 담는 queue라면 팔은 가장 새 보고를 읽어요.

## 문제

controller(팔을 움직이는 프로그램)는 joint state(관절 각도)를 1초에 40번인 40 Hz로 읽는데 driver(모터를 다루는 프로그램)는 100 Hz로 publish합니다. 메시지를 잃지 않으려고 queue depth를 50으로 올렸습니다.

메시지는 10 ms마다 오므로 queue 50개는 0.5초 전까지 거슬러 올라가고 팔은 반 초씩 늦게 반응합니다.

## 개념

두 줄을 보세요. 위쪽은 흐르는 스트림이고 아래쪽은 질문 하나와 답 하나입니다.

![Topics and services](../assets/diagram-ros-parts.png)

*node는 프로그램 하나입니다. topic은 publisher(보내는 쪽)에서 subscriber(받는 쪽)로 가는 스트림을 나릅니다. service는 요청 하나에 응답 하나를 돌려줍니다.*

subscriber는 메시지가 기다리는 줄인 queue를 가집니다. history 설정이 "keep last"이면 queue는 가장 최근 `depth`개를 담고 가득 찬 상태에서 새 메시지가 오면 가장 오래된 메시지가 밀려납니다.

![Slow subscriber](../assets/diagram-queue-depth.png)

*publisher가 더 빠르므로 queue는 가득 찬 채로 있고 publish할 때마다 가장 오래된 메시지가 버려집니다.*

publisher 100 Hz와 reader 40 Hz로 10초를 돌려 봅니다. publisher는 메시지 1000개를 보내고 reader는 depth와 상관없이 400개를 읽습니다.

마지막으로 읽은 메시지는 depth 1에서 5 ms 전 것이고 queue에 메시지가 하나 더 쌓일 때마다 publish 주기 하나인 10 ms가 더해집니다. depth 10은 95 ms, depth 50은 495 ms입니다.

![Three arms, three queue depths](../assets/clip-example.mp4)

*depth마다 팔 한 대씩 세 대입니다. 연한 컵은 그 팔이 컵이 있다고 믿는 자리입니다. 초록(depth 1)은 컵 위에 머물고 연한 파랑(depth 10)은 조금 뒤처지며 파랑(depth 50)은 예전 위치를 쫓아갑니다.*

![Queue depth](../assets/fig-queue-depth.png)

*왼쪽에서는 depth가 클수록 메시지 나이가 커지는 모습을 보세요. 대략 발행 주기 `(depth - 1)`개만큼입니다. 오른쪽은 발행한 1000개 중 400개가 depth와 상관없이 전달됩니다. depth는 나머지 600개를 "버려짐"과 "아직 queue에 있음" 사이에서 옮길 뿐입니다.*

## 만들기

이름 있는 topic과 구독마다 queue 하나를 가진 `Bus`입니다. ROS를 설치할 필요가 없습니다.

```python
def publish(self, topic, msg):
    for s in self.subs.get(topic, []):
        if len(s.q) == s.depth:
            s.q.popleft()
            s.dropped += 1
        s.q.append(msg)
```

`run(pub_hz, sub_hz, depth, seconds)`는 메시지마다 보낸 시각을 찍고 subscriber tick(읽기 한 번)마다 하나씩 꺼냅니다.

그래서 폐기 개수와 읽은 메시지의 나이를 보고합니다. `burst_drops()`는 depth가 도움이 되는 경우, 곧 queue보다 짧은 burst(한꺼번에 몰려오는 메시지)를 보여 줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-setup-and-tooling/04-ros2-in-one-page -q
python3 phases/00-setup-and-tooling/04-ros2-in-one-page/code/main.py
```

## 실제 도구로 보기

ROS 2에서는 같은 설정이 QoS(quality of service) history 정책 `keep last`와 queue depth입니다. QoS 문서가 뒷받침하는 것은 여기까지입니다. 이어지는 조언은 이 레슨의 것입니다.

최신 값만 중요한 제어 신호에는 작은 depth를 두고 burst에 대비할 때만 더 크게 잡습니다. depth를 올리기 전에 subscriber 속도를 publisher에 맞춥니다.

출처: https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-Quality-of-Service-Settings.html

## 결과물

`outputs/skill-qos-depth-check.md`는 topic의 속도와 depth를 보고 데이터가 버려지는지 낡는지 알려 줍니다.

## 연습 문제

1. "keep all" 구독을 추가하고 queue가 어떻게 자라는지 보이세요.
2. subscriber가 publisher보다 빠를 때 메시지 나이를 그래프로 그리세요.
3. 같은 topic에 depth가 다른 두 번째 subscriber를 추가하세요.
