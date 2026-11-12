# 학습 정책을 위한 안전 wrapper (Safety Wrapper)

> 학습된 정책은 무슨 말이든 할 수 있는 producer입니다. 그 뒤의 층은 결정론적이어야 하고 무슨 말이 나왔는지에 흔들리지 않아야 합니다.

**유형:** 만들기   **선수 지식:** 13/02 행동 복제의 함정   **시간:** 약 15분

## 쉽게 말하면

운전 게임의 조향 명령에 필터를 둔다고 해 보세요. 플레이어가 stick을 확 꺾어도 조향 크기와 바뀌는 속도를 제한할 수 있어요. safety wrapper도 학습한 로봇 policy의 명령에 이런 제한을 걸어요.

policy를 부르기 전에 관측이 최신인지 확인해요. 잠깐 끊기면 이전 명령을 유지하고 오래 끊기면 fallback 쪽으로 바꿔요. 유효하지 않은 출력도 바꿔요. 명령은 예측 가능한 규칙을 따르지만 모든 움직임의 안전까지 증명하는 것은
아니에요.

## 문제

시연으로 학습한 정책은 매 tick 명령을 내지만 그 명령이 유한하고 작고 매끄럽고 최근 관측에 근거한다는 보장은 학습 어디에도 없습니다.
spike 하나, NaN 하나, 얼어붙은 카메라 프레임 하나가 최대 속도로 actuator에 닿습니다. 신경망을 테스트로 안전하게 만들 수는 없지만 짧고 결정론적인 층은 테스트할 수 있습니다.

## 개념

![wrapper 파이프라인](../assets/diagram-wrapper-pipeline.png)

*먼저 관측의 나이를 검사하고 쓸 수 있는 관측에서만 정책을 돌립니다. 출력은 아무것도 움직이기 전에 clip하고 변화율을 제한합니다. 바뀐 것은 모두 로그에 남습니다.*

정책은 실행마다 달라질 수 있습니다. wrapper는 그렇지 않아서 같은 입력에는 항상 같은 출력과 같은 로그가 나옵니다. 그래서 평범한 assert와 fuzzing으로 테스트할 수 있습니다.

![hold 다음에 fallback](../assets/diagram-wrapper-ladder.png)

*짧은 공백에는 마지막 명령을 유지합니다. 마감 시한을 넘기면 fallback으로 서서히 내립니다.*

![원시 명령과 wrapper 출력 비교](../assets/fig-wrapper-containment.png)

*점이 x = 1에서 0으로 가야 합니다. wrapper가 없으면 부호가 뒤집힌 burst가 x를 약 3.3까지 던집니다. wrapper가 있으면 x는 1을 넘지 않고 로그에는 개입 45건이 기록됩니다.*

## 만들기

`act()`는 다음 순서로 처리합니다. 오래되었거나 없는 관측을 거르고 정책을 부르고 유한하지 않은 값을 바꾸고 clip하고 변화량을 제한합니다.

```python
raw = policy(obs)
target = fallback if not np.isfinite(raw) else float(np.clip(raw, lo, hi))
out = float(np.clip(target, last_out - max_step, last_out + max_step))
```

fuzz 테스트는 NaN과 무한대를 포함한 무작위 명령 2000개를 보내고 모든 출력이 두 제한을 지키는지 assert합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/04-learned-policy-safety-wrapper -q
python3 phases/13-learning-for-robots/04-learned-policy-safety-wrapper/code/figure.py
```

## 실제 도구로 보기

실제 제어기에는 이미 limiter가 들어 있습니다.
예를 들어 ROS 2 `joint_limits` 패키지는 controller나 하드웨어에서 joint limit을 다루는 인터페이스와, 위치와 속도와 가속도를 위한 saturation limiter를 제공합니다.
wrapper의 나이 검사와 로그는 그 앞에 놓습니다. 그것을 대신하지 않습니다.

출처: ROS Index, `joint_limits` 패키지 페이지(index.ros.org/p/joint_limits). 2026년 11월 9일에 열어 확인했습니다.

## 결과물

`outputs/skill-policy-safety-wrapper.md`는 학습 정책과 actuator 사이의 층을 검토하는 체크리스트입니다.

## 연습 문제

1. 속도에 따라 달라지는 제한을 추가하고 그 fuzz 테스트를 쓰세요.
2. fallback이 `n` tick 동안 0으로 내려가게 하고 `n`이 정지 거리와 맞는지 확인하세요.
3. 기록된 정책 로그를 `Wrapper.act`에 다시 넣어 첫 개입을 찾으세요.
