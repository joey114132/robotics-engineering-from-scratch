# 시간 동기화와 Trace

> 몇 ms 어긋난 두 시계는 센서 데이터의 순서를 뒤집습니다. 전후 상태가 담긴 trace는 실행이 처음 어디서 틀어졌는지 보여 줍니다.

**유형:** 만들기   **선수 지식:** 05/03 제어 Loop Jitter   **시간:** 약 15분

## 쉽게 말하면

자동차에는 컴퓨터가 서로 다른 센서 두 개가 달려 있어요. 움직임을 느끼는 IMU와 길을 보는 카메라예요. 두 센서의 값을 합치는 프로그램인 filter는 각 값에 찍힌 시각을 믿어요.
카메라 시계가 앞서 가면 카메라 값에 미래의 시각이 찍혀서 filter는 사건을 잘못된 순서로 보고 차의 위치가 앞으로 튀었다가 되돌아와요.
시계의 offset을 빼 주면 순서가 바로잡혀요. offset은 요청과 응답에 시각을 적어 재요.

## 문제

fusion filter는 컴퓨터 두 대에서 오는 카메라와 IMU 샘플을 합치는데 추적하는 자동차가 앞으로 튀었다가 되돌아옵니다.
샘플은 모두 맞지만 카메라 시계가 30 ms 앞서 있어서 먼저 찍은 카메라 샘플이 나중에 찍은 IMU 샘플보다 늦은 stamp를 받을 수 있습니다.
나중에 실행이 실패해도 각 step이 상태를 기록해 두지 않았다면 어느 step이 처음 틀어졌는지 아무도 모릅니다.

## 개념

![네 개의 타임스탬프](../assets/diagram-offset-exchange.png)

*번호 1부터 5까지 따라가 보세요. offset은 `t1 - t0`와 `t2 - t3`의 합을 절반으로 나눈 값입니다.*

client는 요청을 t0에 보내고 응답을 t3에 받으며 둘 다 자기 시계로 적습니다. server는 요청을 t1에 받고 t2에 응답하며 둘 다 server 시계로 적습니다.
예를 들어 server 시계가 50 ms 앞서 있고 한 번 가는 데 20 ms가 걸리면 `t1 - t0`는 70 ms이고 `t2 - t3`는 30 ms입니다. 둘의 평균은 50 ms이고 이동 시간이 한쪽에서는 더해지고 다른 쪽에서는 빠지기 때문입니다.
가는 데 30 ms 오는 데 10 ms가 걸리면 60 ms가 나와서 두 지연 차이의 절반만큼 틀립니다. 오차는 왕복 시간의 절반을 넘지 않으므로 왕복이 가장 짧은 교환을 믿습니다.

![offset 추정과 순서 오류](../assets/fig-time-sync.png)

*왼쪽은 8번 중 가장 좋은 교환이 한 번 잰 값보다 오차가 좁은 모습입니다. 오른쪽은 센서 간격이 10 ms일 때 offset이 10 ms를 넘으면 순서가 뒤집히고 1 ms 오차의 추정값은 순서를 복구하는 모습입니다.*

trace는 step마다 JSON 한 줄(글자로 쓴 기록)을 남긴 로그이고 각 줄에 전 상태(`pre`)와 후 상태(`post`)가 들어 있습니다. intent는 그 step이 이루어야 할 일입니다.
reader는 처음 실패한 것을 `not_executed`, `no_motion`(상태가 그대로), `wrong_motion`(엉뚱한 곳에 도착) 중 하나로 부릅니다.

![trace reader](../assets/diagram-trace-reader.png)

*reader는 intent를 순서대로 확인하고 처음 어긋난 곳에서 멈춥니다.*

예를 들어 목표가 세 곳인데 step 2에서 `pre`와 `post`가 같다고 해 보겠습니다. `first_mismatch()`는 step 2와 `no_motion`을 돌려주고 step 3은 보지 않습니다.

![목표 두 번째를 건너뛴 팔, 멈추는 reader](../assets/clip-example.mp4)

*팔이 가운데 목표를 놓칩니다. reader가 첫 번째를 초록, 두 번째를 빨강으로 바꾸고 멈춥니다.*

## 만들기

```python
def estimate(t0, t1, t2, t3):
    return ((t1 - t0) + (t2 - t3)) / 2, (t3 - t0) - (t2 - t1)
```

`order_errors()`는 stamp로 정렬한 순서가 실제 순서와 다른 칸을 셉니다. `trace_line()`은 step마다 JSON 객체 한 줄을 씁니다.

`first_mismatch()`는 처음 실패한 intent를 돌려줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/04-time-sync-and-traces -q
```

## 실제 도구로 보기

`estimate()`를 NTP 규격의 offset과 delay 정의와 비교해 보세요.

출처: RFC 5905와 ROS 2 설계 문서 "Clock and Time".
https://datatracker.ietf.org/doc/html/rfc5905
https://design.ros2.org/articles/clock_and_time.html

둘 다 2026년 11월 9일에 읽었습니다.

## 결과물

`outputs/skill-trace-first-mismatch.md`는 trace를 읽고 처음 실패한 step을 알려 줍니다.

## 연습 문제

1. `first_mismatch()`가 `pre`가 앞 step의 `post`와 다른 step도 표시하게 하세요.
2. 교환마다 `proc` 시간을 넣고 `estimate()`가 그것을 무시한다는 것을 보이세요.
3. 1분 간격으로 잰 offset에서 drift 비율을 맞추고 1시간 뒤의 offset을 예측하세요.
