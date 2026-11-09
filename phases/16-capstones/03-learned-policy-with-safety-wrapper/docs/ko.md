# 안전 wrapper를 두른 학습 정책

> 학습된 정책은 가끔 틀려도 됩니다. 그래서 주변 코드는 틀렸을 때도 위험하지 않게 만들어야 합니다.

**유형:** 만들기   **선수 지식:** 03/01 샘플링 한계, 03/04 PID와 튜닝   **시간:** 약 30분

## 문제

시연 데이터로 학습한 정책이 모든 테스트에서는 잘 돕니다. 그러다 나쁜 출력 하나나 유실된 프레임 하나에 관절이 한계로 달려갑니다. 학습된 모델이 절대 그러지 않는다는 것은 증명할 수 없습니다. 대신 모델과 모터 사이에 작은 일반 코드를 끼우고 그 코드를 증명할 수 있습니다.

## 개념

![안전 wrapper 안의 학습 정책](../assets/diagram-policy-system.png)

*시연이 nearest-neighbour 정책을 학습시킵니다. 정책의 action은 관절에 닿기 전에 wrapper를 지납니다. wrapper는 관측이 얼마나 오래됐는지도 봅니다.*

![고장 두 개와 wrapper 하나](../assets/diagram-policy-broken.png)

*spike는 clip과 변화율 제한으로 막습니다. 유실된 관측은 너무 오래되면 hold 명령이 됩니다.*

![작업이 성공하는 모습](../assets/fig-policy-result.png)

*깨끗한 실행에서 복제 정책은 expert처럼 목표에 도착합니다. wrapper는 처음 토크가 올라가는 구간만 늦춥니다.*

![wrapper가 있을 때와 없을 때의 고장](../assets/fig-policy-faults.png)

*spike에서는 최대 토크가 wrapper 없이 40 Nm, 있으면 3 Nm이고 관절 최대각은 1.36 rad 대 1.01 rad입니다. 관측 유실에서는 1.47 rad 대 1.01 rad입니다. 한계는 1.3 rad입니다.*

## 만들기

wrapper는 정해진 순서의 규칙 세 개입니다. 관측이 낡았으면 먼저 hold합니다. 그다음 토크 한계로 clip하고 step당 변화량을 제한합니다.

```python
if age > self.max_age: raw = 0.0
c = np.clip(raw, -self.umax, self.umax)
r = self.u + np.clip(c - self.u, -self.du, self.du)
```

규칙마다 action을 몇 번 바꿨는지 셉니다. 이 횟수가 증거입니다. spike 실험은 clip 1회, 관측 유실 실험은 hold 23 step, 깨끗한 실행은 clip과 hold가 0회입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/16-capstones/03-learned-policy-with-safety-wrapper -q
python3 phases/16-capstones/03-learned-policy-with-safety-wrapper/code/main.py
```

## 실제 도구로 보기

ros2_control은 hardware interface에 대한 joint limit 처리를 제공합니다. `ros2_control_node`의 `enforce_command_limits` 파라미터가 모든 interface의 joint limit 처리를 전역으로 정합니다.

시작할 때 controller manager가 joint마다 어떤 limit이 있는지 로그로 남깁니다. 그 목록을 여기의 규칙 세 개와 비교해 보세요.

출처: [ros2_control joint limiting](https://control.ros.org/rolling/doc/ros2_control/hardware_interface/doc/joint_limiting.html)
2026년 11월 9일 확인.

## 결과물

`outputs/skill-policy-wrapper-audit.md`는 학습 정책을 감싼 wrapper가 범위, 변화율, 낡은 관측을 모두 다루는지 점검합니다.

## 연습 문제

1. 관측 유실 실험이 처음 1.3 rad를 넘을 때까지 `max_age`를 올려 보세요.
2. 네 번째 규칙으로 속도 제한을 넣고 개입 횟수를 세어 보세요.
3. 40개 대신 5개 episode로 학습시키고 wrapper가 어느 고장을 더 자주 막는지 보세요.
