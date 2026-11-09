# PID와 튜닝 (PID and Tuning)

> P는 지금 밀고 I는 과거를 기억하고 D는 브레이크를 겁니다. 각각 한 문제를 풀고 다른 문제를 만듭니다.

**유형:** 만들기   **선수 지식:** 03/01 샘플링 한계, 03/03 임피던스 제어   **시간:** 약 15분

## 문제

관절이 진동해서 누군가 `kp`와 `kd`를 올려 뻣뻣하게 만들었습니다. 이제 관절이 윙윙거리고 모터가 뜨거워집니다. PID gain은 서로 독립인 세 개의 손잡이처럼 보이지만 각각은 plant와 액추에이터와 제어 주기가 정하는 한계를 가집니다.

## 개념

![세 항을 더한 뒤 액추에이터가 잘라 냅니다](../assets/diagram-pid-structure.png)

*관절에는 관성 `J`와 마찰 `b`와 부하가 있습니다. 컨트롤러는 측정된 각도와 속도만 봅니다.*

![P만 쓰면 떨리고 P+D는 오프셋을 남기며 멈추고 P+I+D가 오프셋을 없앱니다](../assets/fig-pid-terms.png)

*5초에 부하가 걸립니다. P+D에서는 관절이 목표보다 `load / kp`만큼 아래에서 멈춥니다. 적분 항만 관절을 되돌립니다.*

적분 항은 오차를 더해 가므로 액추에이터가 한계에 있는 동안에도 계속 더합니다. 이것이 windup입니다.

![액추에이터가 포화된 동안 적분 항이 쌓입니다](../assets/diagram-windup.png)

*여기서 쓰는 해법은 조건부 적분입니다. 포화되어 있고 오차가 더 깊이 밀 때는 적분을 멈춥니다.*

![windup overshoot와 clamp를 건 적분기 비교](../assets/fig-windup.png)

*gain과 토크 한계는 같습니다. clamp가 없으면 관절이 목표를 약 1.5 rad 넘어갑니다.*

gain을 올릴 때는 두 번째 한계가 있습니다. tick마다 명령을 하나 붙잡는 loop는 2x2 갱신 행렬의 고유값이 단위원 안에 있을 때만 안정합니다. 레슨 03/01과 같은 이야기입니다. `kd`가 약 `2J/dt`를 넘으면 명령이 tick마다 부호를 뒤집습니다.

![올린 gain은 명령을 덜덜 떨게 하고 고유값이 그 이유를 보여 줍니다](../assets/fig-raised-gains.png)

*왼쪽은 gain을 바꾼 뒤의 토크 명령입니다. 오른쪽은 가장 큰 고유값 크기가 `kd = 2J/dt` 근처에서 1을 넘는 모습입니다.*

## 만들기

```python
raw = kp * e + I - kd * v
u = np.clip(raw, -umax, umax)
if u == raw or e * raw < 0:      # conditional integration
    I += ki * e * dt
v += dt / J * (u - b * v - load)
```

`simulate()`가 이 loop를 돌립니다. `closed_loop_matrix()`와 `spectral_radius()`가 안정성 검사를 맡습니다.

테스트는 오프셋 `load / kp`, I와 D의 효과, clamp를 건 windup 비교를 확인하고 두 gain 조합 모두에서 고유값이 발산 여부를 맞히는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/04-pid-and-tuning -q
python3 phases/03-dynamics-and-control/04-pid-and-tuning/code/figure.py
```

## 실제 도구로 보기

ROS 2 `control_toolbox`는 `none`, `back_calculation`, `conditional_integration` anti-windup 전략을 줍니다.

관절마다 하나를 고르는 설정은 `pid_controller` 사용자 문서의 `gains.<dof_names>.antiwindup_strategy`입니다.

자기 plant에서 그 conditional integration을 이 레슨의 clamp와 비교해 보세요. 오프셋 논증은 Craig 9장(9.7절, disturbance rejection)에 있습니다.

출처 (2026년 11월 9일 확인)

- [control_toolbox 문서](https://control.ros.org/master/doc/control_toolbox/doc/index.html): 전략 세 가지
- [PID controller 사용자 문서](https://control.ros.org/rolling/doc/ros2_controllers/pid_controller/doc/userdoc.html): 관절별 설정

## 결과물

`outputs/skill-pid-tuning-check.md`는 gain 변경을 오프셋과 windup과 샘플링 한계 관점에서 점검합니다.

## 연습 문제

1. 조건부 적분을 back-calculation으로 바꾸고 overshoot를 비교하세요.
2. 미분을 속도 대신 오차에 걸고 setpoint step에서 어떻게 되는지 보세요.
3. `kd = 20`에서 spectral radius를 1 아래로 유지하는 가장 큰 `kp`를 찾으세요.
