# 제어 Loop Jitter

> loop의 평균 주기가 완벽해도 수천 번에 한 번 늦게 깨어나는 것이 제어기를 깨뜨릴 수 있습니다.

**유형:** 만들기   **선수 지식:** 05/02 Executor와 Callback   **시간:** 약 15분

## 쉽게 말하면

control loop는 박자마다 로봇 팔에 새 목표를 줘요. 메트로놈과 비슷해요. 이전 동작이 끝난 뒤 한 주기를 쉬고 다음 박자를 잡으면 박자가 갈수록 조금씩 늦어져서 팔이 뒤처져요.
박자를 시계의 정해진 시각에 고정하면 박자가 일정하게 유지돼요. 그래도 아주 가끔 다른 프로그램이 processor를 붙잡아 깨어나는 시각이 한 번 늦어지고 팔이 떨려요.
평균은 그 늦은 박자 하나를 숨기니 최악의 지연과 놓친 deadline도 함께 확인해야 해요.

## 문제

1 kHz control loop는 1초에 1000번 깨어나 팔에 명령을 줍니다. 이 loop의 평균 주기는 정확히 1.000 ms로 보고되는데 팔은 몇 초에 한 번씩 떨립니다.
평균은 정상 cycle 수천 개를 합친 값이라 나쁜 cycle 하나는 평균을 거의 움직이지 못합니다. 그런데 떨림은 바로 그 나쁜 cycle 하나에서 나옵니다.

## 개념

![고정 주기 loop의 한 바퀴](../assets/diagram-loop-anatomy.png)

*번호를 따라가 보세요. 한 바퀴는 정해진 시각까지 자고 조금 늦게 깨어나 일하며 다음 deadline, 즉 다음 바퀴가 시작되어야 하는 시각 전에 끝나야 합니다.*

jitter는 실제 주기에서 목표 주기 T를 뺀 값입니다. `i * T`(i번째 바퀴에 정해진 시각)까지 자면 평균이 T로 유지되므로 늦게 깨어나는 일은 퍼짐으로만 나타납니다. 일을 끝낸 뒤 T를 쉬면 일한 시간이 매 cycle에 더해져서 loop가 점점 느려집니다.

![평균과 최악의 비교](../assets/diagram-average-hides.png)

*평균과 표준편차는 물론 p99(전체 cycle의 99%가 넘지 않는 지연)까지도 멀쩡해 보일 수 있습니다. 모터를 움직이는 것은 가장 나쁜 cycle 하나입니다.*

예를 들어 이 실행에서 2098번째 cycle은 1.5 ms 늦게 깨어납니다. 일 0.2 ms가 다음 칸보다 0.7 ms 뒤에 끝나므로(1.5 + 0.2 - 1.0) 다음 cycle도 0.7 ms 늦게 시작합니다.
그래서 팔에 가는 명령이 늦게 나가고 목표는 이미 움직였는데 팔은 기다립니다.

![늦게 깨어난 한 번에 목표에 뒤처지는 팔](../assets/clip-example.mp4)

*팔과 호박색 공을 보세요. 공은 정해진 시각에 한 칸씩 움직이고 팔은 명령이 실제로 나간 시각에 움직이므로 한 번 뒤처졌다가 따라잡습니다. 움직임을 10 cycle 길이로 그렸고 450배 느리게 재생했습니다.*

![jitter 히스토그램과 시간선](../assets/fig-jitter.png)

*seed로 난수를 고정한 5000 cycle 실행에서 평균 jitter는 0 us(마이크로초)이고 p99는 113 us이지만 최악은 1498 us, 즉 약 1.5 ms이고 deadline을 5번 놓칩니다.*

## 만들기

```python
wake = (done + T if relative else i * T) + lat[i]
s[i] = max(wake, done)
d[i] = done = s[i] + work
```

`simulate()`는 작은 무작위 wake-up 지연(지수분포)에 주기의 0.5배에서 1.5배 사이의 드문 spike를 더합니다.

`stats()`는 평균, p99, 최악 jitter를 내고 다음 deadline 뒤에 끝난 iteration을 셉니다. spike는 선점(preemption)을 흉내 낸 모델이고 측정값이 아닙니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/05-robot-software/03-control-loop-jitter -q
python3 phases/05-robot-software/03-control-loop-jitter/code/main.py
```

## 실제 도구로 보기

Linux에서 `clock_nanosleep`에 `TIMER_ABSTIME`을 주면 절대 시각까지 잡니다. 이 레슨의 `i * T` 방식입니다. 시뮬레이션의 최악값을 믿기 전에 자기 loop에서 잰 값과 비교해 보세요.

출처: clock_nanosleep(2)와 ROS 2 Jazzy "Understanding real-time programming".
https://man7.org/linux/man-pages/man2/clock_nanosleep.2.html
https://docs.ros.org/en/jazzy/Tutorials/Demos/Real-Time-Programming.html

둘 다 2026년 11월 9일에 읽었습니다.

## 결과물

`outputs/skill-loop-jitter-report.md`는 loop 타임스탬프 목록을 평균, p99, 최악, miss 보고서로 바꿉니다.

## 연습 문제

1. `spike_p`를 올려서 p99도 나빠 보이게 만들고 그때 cycle이 몇 개인지 적으세요.
2. 각 miss 바로 다음 주기를 찾고 왜 평소보다 짧은지 설명하세요.
3. 연속 miss 두 번에 작동하는 watchdog을 넣고 얼마나 자주 작동하는지 보고하세요.
