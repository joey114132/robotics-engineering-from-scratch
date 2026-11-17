# 학습된 policy를 위한 안전 wrapper (Safety Wrapper)

> 학습된 모델과 모터 사이에 단순하고 검증할 수 있는 안전 장치를 두는 법을 배웁니다.

**유형:** 만들기   **선수 지식:** 13/02 행동 복제의 함정   **시간:** 약 15분

## 쉽게 말하면

장난감 자동차의 속도 명령은 학습된 policy(예시로 훈련한 모델)가 내는데 이 policy는 가끔 엉뚱한 값을 내요. safety wrapper는 모터 앞에서 명령을 작게 하고 천천히 바뀌게 해요.

카메라 영상이 오래됐으면 wrapper는 마지막 명령을 되풀이하다가 자동차를 서서히 멈춰 세워요.

## 핵심 용어

- **Safety wrapper**: policy와 모터 사이에 놓여 모든 명령을 제한하는 고정된 층입니다.
- **Tick**: 제어 한 번의 주기입니다. 보고 정하고 명령하는 한 바퀴입니다.
- **Clip**: 값을 범위 안으로 잘라 넣는 것입니다.
- **Rate limit**: tick 한 번에 명령이 바뀔 수 있는 크기의 상한입니다.
- **Fallback**: 화면이 너무 오래됐을 때 쓰는 안전한 명령입니다. 여기서는 정지입니다.
- **Fuzzing**: 코드가 깨지는지 보려고 무작위 입력을 마구 던지는 시험입니다.

## 문제

학습된 모델이 장난감 자동차를 몰다가 가끔 NaN(숫자가 아님)이나 터무니없는 속도를 내거나 카메라가 얼어붙어 낡은 화면으로 계속 움직입니다. 그 명령이 최대 속도로 모터에 닿습니다.

## 개념

학습된 모델은 예상 밖의 일을 하므로 사람을 다치게 할 수 있는 로봇에는 절대 예상 밖의 일을 하지 않는 안전 장치가 필요합니다. wrapper는 평범한 코드입니다.
화면이 얼마나 오래됐는지 보고 명령을 안전한 범위로 자르고 명령이 바뀌는 속도를 제한합니다. 평범하기 때문에 세게 시험할 수 있습니다.

![wrapper 파이프라인](../assets/diagram-wrapper-pipeline.png)

*화면의 나이를 보고 신선한 화면에서만 policy를 돌린 뒤 명령을 자르고 느리게 만듭니다.*

![사다리](../assets/diagram-wrapper-ladder.png)

*조금 오래된 화면에는 마지막 명령을 되풀이하고 아주 오래된 화면에는 정지로 서서히 내립니다.*

![억제](../assets/fig-wrapper-containment.png)

*wrapper가 없으면 명령이 반대로 뒤집힌 burst가 자동차를 목표 너머로 멀리 던집니다. wrapper가 있으면 거의 움직이지 않습니다.*

![화살표가 달린 자동차들](../assets/clip-example.mp4)

*주황색 화살표는 모터가 받는 명령입니다. 파랑 자동차는 엉뚱한 값을 그대로 받아 뒤로 튕겨 나가고 초록 자동차의 화살표는 작게 머뭅니다.*

<details><summary>The math (optional)</summary>

tick 한 번은 0.05초입니다. 10 tick 마감 시한을 넘기면 fallback으로 서서히 내립니다. 점이 x = 1에서 0으로 가야 하는데 부호가 뒤집힌 burst가 x를 약 3.3까지 던집니다.
wrapper가 있으면 x는 1을 넘지 않고 개입 45건이 기록됩니다. tick 20에 지금까지 -0.48로 표시선 쪽을 향하던 policy가 부호가 뒤집힌 8.0을 8 tick 동안 냅니다.
wrapper는 이 값을 1.0으로 clip하고 명령이 tick마다 0.2씩만 오르게 해서 -0.28, -0.08, 0.12가 됩니다.
wrapper가 있는 자동차는 x = 0.22에서 0.38까지만 움직이고 없으면 0.12에서 3.32까지 날아갑니다.

</details>

## 만들기

`act()`는 오래된 화면을 거르고 policy를 부르고 NaN이나 무한대를 바꾸고 clip하고 변화량을 제한합니다.

```python
raw = policy(obs)
target = fallback if not np.isfinite(raw) else float(np.clip(raw, lo, hi))
out = float(np.clip(target, last_out - max_step, last_out + max_step))
```

fuzz 테스트는 NaN을 포함한 무작위 명령 2000개를 보내고 두 제한이 지켜지는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/04-learned-policy-safety-wrapper -q
python3 phases/13-learning-for-robots/04-learned-policy-safety-wrapper/code/figure.py
```

## 실제 도구로 보기

실제 제어기에는 이미 limiter가 들어 있습니다. ROS 2(로봇 소프트웨어 프레임워크)의 `joint_limits`가 그 예입니다. 

출처: ROS Index, `joint_limits`(index.ros.org/p/joint_limits). 2026년 11월 9일에 열어 확인했습니다.

## 결과물

`outputs/skill-policy-safety-wrapper.md`는 policy와 모터 사이의 층을 검토합니다.

## 연습 문제

1. 자동차가 빠를수록 제한이 작아지게 하고 fuzz하세요.
2. fallback이 0으로 내려가는 tick 수를 바꿔 보세요.
3. 기록된 policy 로그를 `Wrapper.act`에 다시 넣으세요.
