# 토크 모드와 position 모드 (Torque vs Position Modes)

> position 모드는 남의 PD gain을 쓰는 토크 모드이고 그 gain이 관절이 얼마나 뻣뻣하게 느껴지는지를 정합니다.

**유형:** 만들기   **선수 지식:** 04/01 모터와 기어박스, 03/03 임피던스 제어   **시간:** 약 15분

## 문제

관절이 `K = 20`인 부드러운 스프링처럼 움직이게 하는 impedance controller를 짭니다. 그런데 가진 drive에서는 관절이 뻣뻣하게 버티고 밀어도 거의 움직이지 않습니다.
바깥 loop는 부드러움을 요청했지만 drive 자신의 position loop에는 그 요청이 전달되지 않았기 때문입니다.

## 개념

![누가 loop를 닫는가](../assets/diagram-mode-loops.png)

*토크 모드에서는 내 loop가 토크를 씁니다. position 모드에서는 drive의 안쪽 PD가 쓰고 그 gain은 바꿀 수 없습니다.*

일정한 외력 `tau_ext`가 있으면 관절은 스프링 힘이 외력과 균형을 이루는 곳에 멈춥니다. 토크 모드에서는 `tau_ext / K`이므로 `K`를 내가 고릅니다. position 모드에서는 `K`로 무엇을 보내든 `tau_ext / kp_in`입니다.

![바깥 controller가 요청할 수 있는 것](../assets/diagram-mode-options.png)

*impedance에는 토크 인터페이스가 필요합니다. position만 되는 drive는 바깥에 compliance 층이 필요하고 그 층에는 측정한 토크가 필요합니다.*

![외력에 대한 응답과 느껴지는 강성](../assets/fig-mode-stiffness.png)

*왼쪽은 같은 2 Nm 외력이 세 가지 전혀 다른 관절을 만드는 모습입니다. 오른쪽은 요청한 강성을 그대로 느끼는 것은 토크 모드뿐이고 admittance 층은 안쪽 gain보다 낮게 묶인다는 것을 보여 줍니다.*

## 만들기

관절 하나 `J*qdd = tau - b*qd + tau_ext`에 `tau`를 만드는 방법이 세 가지입니다.

```python
if mode == "torque":
    tau = K * (q_des - q) - D * qd
elif mode == "position":
    tau = kp_in * (q_des - q) - kd_in * qd
elif mode == "admittance":
    tau = kp_in * (q_des + ext / K - q) - kd_in * qd
```

테스트는 `position`이 `K = kp_in, D = kd_in`인 `torque`와 같다는 것을 보입니다. admittance의 처짐은 `tau_ext * (1/K + 1/kp_in)`입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/04-actuators-and-sensors/02-torque-vs-position-modes -q
python3 phases/04-actuators-and-sensors/02-torque-vs-position-modes/code/figure.py
```

## 실제 도구로 보기

ros2_control에서는 관절마다 command 인터페이스를 선언하며 보통 position, velocity, acceleration, effort 중 하나입니다. controller가 hardware가 제공하지 않는 인터페이스를 요청하면 실패합니다.
impedance와 admittance 중 무엇을 쓸지 정하기 전에 drive가 어떤 인터페이스를 내보내는지 확인하세요.

출처 (2026년 11월 9일 접속):

- [ros2_control full tutorial](https://control.ros.org/master/doc/ros2_control_demos/example_7/doc/userdoc.html)

## 결과물

`outputs/skill-drive-mode-check.md`는 drive가 impedance 제어를 바로 올릴 수 있는지 판정합니다.

## 연습 문제

1. `kp_in`을 4000으로 올리고 admittance 처짐이 어떻게 변하는지 재세요.
2. 측정한 외력에 3 ms 지연을 넣고 admittance loop를 보세요.
3. admittance 층이 요청의 절반만큼만 뻣뻣하게 느껴지는 `K`를 찾으세요.
