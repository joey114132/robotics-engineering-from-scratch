# PID와 튜닝 (PID and Tuning)

> 가장 흔한 컨트롤러의 세 부분이 각각 하는 일과, gain을 올리면 무엇이 잘못되는지를 배웁니다.

**유형:** 만들기   **선수 지식:** 03/01 샘플링 한계, 03/03 임피던스 제어   **시간:** 약 15분

## 쉽게 말하면

P, I, D 세 부분을 가진 컨트롤러가 장난감 자동차를 정지선에 세운다고 해 보세요. P는 차가 선에서 멀수록 더 세게 밀어요. D는 빠를수록 더 세게 브레이크를 걸어요. I는 차가 선에 못 미친 채로 오래 있을수록 미는 힘을 더해요. 그래서 계속 부는 맞바람도 이겨 내요.

페달을 끝까지 밟고 있어도 I는 못 미친 만큼을 계속 쌓아요. 그러다 나중에 차를 선 너머로 밀어 버려요. anti-windup은 이것을 막아요.

## 핵심 용어

- **PID**: P(오차), I(시간에 따라 쌓은 오차), D(속도에 거는 브레이크) 세 부분으로 조종하는 방법입니다.
- **Gain**: 컨트롤러가 얼마나 세게 반응하는지입니다. 예를 들어 오차 한 단위당 미는 힘입니다.
- **Steady offset**: 어떤 힘이 관절을 계속 미는데 P와 D만 일할 때 남는 오차입니다.
- **Saturation**: 모터가 토크 한계에 닿아서 더 세게 밀 수 없는 상태입니다.
- **Windup**: 포화된 동안 I 부분이 계속 쌓였다가 overshoot를 일으키는 현상입니다.
- **Stable**: 윙윙거리거나 폭주하지 않고 가라앉는 loop입니다.

## 문제

로봇 관절이 흔들려서 누군가 미는 힘과 브레이크의 세기(gain)를 올렸습니다. 이제 관절이 윙윙거립니다. gain은 마음대로 돌릴 수 있는 손잡이처럼 보이지만 관절의 무게, 모터의 힘, 제어 주기가 모두 gain에 한계를 정합니다.

## 개념

로봇 관절 대부분은 PID 제어를 쓰므로 각 부분이 무엇을 하고 어디서 실패하는지 알아야 합니다. P는 오차에 비례해서 밀고 D는 속도에 비례해서 브레이크를 겁니다. I는 오차를 시간에 따라 쌓습니다.

![세 항과 하나의 한계](../assets/diagram-pid-structure.png)

*세 항이 더해지고 모터가 그 합을 잘라 냅니다.*

![P, P+D, P+I+D](../assets/fig-pid-terms.png)

*일정한 부하가 걸리면 I만 관절을 되돌립니다.*

![일정한 힘이 밀어도 선을 지키려는 장난감 자동차 두 대](../assets/clip-example.mp4)

*일정한 힘으로 밀면 파랑(P와 D)은 선에 못 미치고 초록(I 포함)은 돌아옵니다.*

그런데 I는 모터가 한계에 있어도 계속 쌓다가 그 빚을 갚느라 지나칩니다. 이것이 windup입니다.

![windup이 적분 항을 쌓습니다](../assets/diagram-windup.png)

*해법은 한계에서 쌓는 것을 멈추는 것입니다.*

![windup과 clamp를 건 적분기](../assets/fig-windup.png)

*주황색은 이 해법을 쓰지 않아서 지나칩니다.*

![올린 gain은 명령을 떨게 합니다](../assets/fig-raised-gains.png)

*gain이 너무 높으면 명령이 단계마다 뒤집힙니다.*

<details><summary>The math (optional)</summary>

일정한 부하는 P+D에서 offset `load / kp`를 남깁니다. `kp = 100`이고 힘이 20이면 offset은 `20 / 100 = 0.2`이고 부하는 5초에 걸립니다. clamp가 없으면 windup으로 약 1.5 rad 지나칩니다.
ROS 2 `control_toolbox`는 anti-windup 방식으로 `none`, `back_calculation`, `conditional_integration`을 제공하고 `gains.<dof_names>.antiwindup_strategy`로 관절마다 고릅니다.
loop는 2x2 갱신 행렬의 고유값(각 움직임 패턴이 tick마다 몇 배가 되는지) 크기가 모두 1보다 작을 때만 안정합니다. `kd`가 약 `2J/dt`를 넘으면 이 조건이 깨집니다(Craig 9.7).

</details>

## 만들기

네 줄이 컨트롤러 전부입니다.

```python
raw = kp * e + I - kd * v
u = np.clip(raw, -umax, umax)
if u == raw or e * raw < 0:      # conditional integration
    I += ki * e * dt
v += dt / J * (u - b * v - load)
```

`simulate()`가 loop를 돌리고 `spectral_radius()`가 안정성 검사를 맡습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/04-pid-and-tuning -q
python3 phases/03-dynamics-and-control/04-pid-and-tuning/code/figure.py
```

## 실제 도구로 보기

ROS 2의 control toolbox에는 만들어진 anti-windup이 있습니다. 이 레슨의 clamp와 비교해 보세요.

출처: [control_toolbox 문서](https://control.ros.org/master/doc/control_toolbox/doc/index.html), [PID controller 사용자 문서](https://control.ros.org/rolling/doc/ros2_controllers/pid_controller/doc/userdoc.html), 2026년 11월 9일 확인.

## 결과물

`outputs/skill-pid-tuning-check.md`는 gain을 바꿨을 때 offset, windup, 샘플링 한계를 점검합니다.

## 연습 문제

1. clamp를 빼고 overshoot를 보세요.
2. 명령이 단계마다 뒤집힐 때까지 `kd`를 올려 보세요.
3. 윙윙거림이 멈출 때까지 `kd`를 낮춰 보세요.
