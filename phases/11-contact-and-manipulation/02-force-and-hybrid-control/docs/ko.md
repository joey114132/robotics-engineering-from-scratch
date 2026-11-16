# 힘 제어와 하이브리드 제어 (Force and Hybrid Control)

> 로봇이 얼마나 무른지 모르는 표면을 알맞은 힘으로 누르는 방법을 알아봅니다.

**유형:** 만들기   **선수 지식:** 11/01 접촉 모델   **시간:** 약 15분

## 쉽게 말하면

스펀지로 책상을 닦을 때는 옆으로 움직이면서 아래로 눌러요. 같은 깊이까지 눌러도 스펀지가 더 무르면 힘이 달라져요.

force control은 누르는 힘을 재고 약하면 더 들어가고 강하면 물러나요. hybrid control은 미끄러지는 방향에는 위치 목표를 주고 누르는 방향에는 힘 목표를 줘요. 그래서 도구가 굴곡을 따라가면서도 누르는 힘을 유지해요.

## 핵심 용어

- **Force control**: 계획한 위치가 아니라 잰 힘에 따라 도구를 움직이는 제어입니다.
- **Hybrid control**: 어떤 축은 위치 제어로, 나머지 축은 힘 제어로 다루는 방식입니다.
- **Stiffness (`ke`)**: 표면을 1 m 눌렀을 때 되미는 힘(N)입니다.
- **Gain (`ki`)**: 힘 오차를 도구 속도로 바꾸는 배율입니다.
- **Time constant**: 오차가 약 3분의 2만큼 줄어드는 데 걸리는 시간입니다.
- **Selection matrix (`S`)**: 축마다 힘 법칙과 위치 법칙 중 하나를 고르는 스위치입니다.

## 문제

로봇이 스펀지를 10 N으로 누른다고 상상해 보세요. 5000 N/m로 가정하고 2 mm만큼 누르라고 명령하지만 스펀지 윗면이 0.4 mm 낮아서 1.6 mm만 눌립니다. 그러면 1000 N/m는 1.6 N, 5000 N/m는 8 N, 25000 N/m는 40 N이 됩니다.

![팔 세 대](../assets/clip-example.mp4)

*같은 깊이로 스펀지 세 개를 누릅니다(어두울수록 뻣뻣함). 빨간 막대는 힘이고 1 N에 1.6 cm입니다.*

## 개념

닦거나 갈아 내는 실제 로봇은 정확히 잴 수 없는 표면에서 일정한 위치가 아니라 일정한 힘이 필요합니다.

![위치 제어의 실패](../assets/diagram-position-miss.png)

*명령은 가정한 강성과 표면 높이에서만 맞습니다.*

![강성에 따른 힘](../assets/fig-force-vs-stiffness.png)

*왼쪽은 힘 루프가 모든 표면에서 10 N에 도달하는 모습입니다. 오른쪽은 위치 제어의 힘이 강성에 따라 커지는 모습입니다.*

힘 루프는 공구 끝을 속도 `v = ki * (fd - f)`로 움직입니다.
`fd`는 원하는 힘이고 `f`는 잰 힘입니다.
spring 표면 `f = ke * x`에서는 `f_dot = ke * ki * (fd - f)`가 됩니다(`f_dot`는 힘이 변하는 빠르기입니다). 차이는 overshoot 없이 `1 / (ke * ki)`초마다 약 3분의 2씩 줄어듭니다.
`dt`마다 갱신하면 차이에 `1 - ke * ki * dt`가 곱해지므로 `ke * ki * dt < 2`일 때만 안정합니다.

실제 작업은 두 법칙이 동시에 필요하므로 선택 행렬 `S`가 각 축에 법칙을 하나씩 줍니다. `S = 1`인 축에서는 힘 법칙이, `S = 0`인 축에서는 위치 법칙이 돕니다.

![하이브리드 선택](../assets/diagram-hybrid-selection.png)

*x 방향은 위치 제어, y 방향은 힘 제어입니다.*

![범프 표면](../assets/fig-hybrid-bumpy.png)

*왼쪽은 하이브리드 도구 경로가 범프를 따르는 모습입니다. 오른쪽은 힘이 0에서 20 N까지 흔들리지 않고 10 N 근처에 머무는 모습입니다.*

## 만들기

하이브리드 법칙은 한 줄입니다. `v_pos`와 `v_frc`는 모든 축에서 계산한 두 법칙의 속도입니다.

```python
v = (1 - S) * v_pos + S * v_frc
p = p + np.clip(v, -lim, lim) * dt
```

가정은 정확한 속도 추종, 마찰 없는 선형 spring 표면, 잡음과 지연 없는 힘 측정입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/11-contact-and-manipulation/02-force-and-hybrid-control -q
python3 phases/11-contact-and-manipulation/02-force-and-hybrid-control/code/main.py
```

## 실제 도구로 보기

MuJoCo에서 soft contact 평면을 두고 같은 누르기를 돌립니다. 정착한 힘을 `ke * depth`와 비교합니다.

출처: Craig(11장)와 원 논문은 출판사 페이지가 403을 돌려주어 열어 보지 못했으므로 둘 다 대조하지 않았습니다.

## 결과물

`outputs/skill-force-control-check.md`는 접촉 작업에서 강성에 민감한 명령과 높은 루프 gain을 점검합니다.

## 연습 문제

1. `K_EST`를 실제 강성으로 바꾸면 위치 제어도 10 N을 내지만 그 표면에서만 그렇다는 것을 보이세요.
2. `dt = 1 ms`에서 `ke = 2.5e4`가 안정하도록 하는 가장 큰 `KI`를 찾으세요.
3. 힘 측정에 10 ms 지연을 더하고 안정 한계를 다시 재세요.
