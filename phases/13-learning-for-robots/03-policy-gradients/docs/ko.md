# 정책 경사 (Policy Gradients)

> 평균보다 높은 점수를 받은 행동 쪽으로 policy를 밀면 됩니다. 대가는 들쭉날쭉한 추정이고 baseline이 그것을 가라앉힙니다.

**유형:** 만들기   **선수 지식:** 13/01 시연으로부터의 모방   **시간:** 약 15분

## 쉽게 말하면

장난감 자동차가 선 위에 멈춰야 하는데 방법은 아무도 알려 주지 않아요. 시도마다 선에 가까이 멈출수록 높은 점수만 줘요. 그다음 점수가 높았던 시도의 움직임이 더 자주 나오도록 조향 규칙을 바꿔요.

시도마다 큰 기본 점수를 똑같이 받는다고 해 보세요. 전체 점수만큼 움직임을 밀어 올리면 모든 움직임이 올라가고 중요한 작은 차이는 기본 점수에 묻혀요. 다른 시도들의 평균 점수를 빼면 평균보다 나은 움직임은 올라가고 못한 움직임은 내려가요.

## 문제

전문가는 없고 reward만 있을 때가 있습니다. 무작위 행동을 해 보고 잘된 쪽으로 움직입니다.
에피소드(처음부터 끝까지 한 번 해 보는 시도) 하나의 return(reward의 합)은 들쭉날쭉해서 같은 설정으로 학습해도 두 실행이 전혀 다르게 보일 수 있습니다.

## 개념

![REINFORCE 루프](../assets/diagram-reinforce-loop.png)

*번호를 따라가 보세요. 행동을 뽑아 reward를 더하고 각 행동의 미는 방향에 그 return을 곱한 뒤 `w`와 `b`를 바꿉니다.*

policy는 Gaussian(종 모양으로 무작위하게 고르는 분포)입니다. 위치가 `x`일 때 자동차는 `w*x + b` 근처로 조향하고 거기에 작은 무작위 탐험 noise가 더해집니다. `w`와 `b`는 학습이 바꾸는 두 숫자입니다.
행동마다 미는 방향(코드의 `score()`)이 있고 그것은 그 행동의 log probability를 미분한 값입니다. 그 행동이 더 자주 나오려면 `w`와 `b`를 어느 쪽으로 돌릴지 알려 줍니다.
여기에 return을 곱해 에피소드에 걸쳐 평균하면 기대 return의 gradient를 추정할 수 있습니다.

![baseline이 바꾸는 것](../assets/diagram-baseline-effect.png)

*모든 return이 크고 양수이면 행동이 전부 위로 밀리고 신호는 그 차이 속에 숨습니다. baseline은 이 퍼짐을 줄이고 탐험 noise는 줄이지 않습니다.*

![학습 곡선과 gradient 분산](../assets/fig-reinforce-baseline.png)

*왼쪽은 seed(무작위 값이 다른 반복 실험) 열 개씩입니다. baseline을 쓴 실행은 꾸준히 오르고 raw(baseline 없음) 실행은 흔들립니다.
오른쪽은 처음 상태에서 두 추정기의 평균이 같고 baseline이 퍼짐, 즉 추정값이 튀는 정도를 약 3분의 1로 줄이는 모습입니다.*

같은 출발점에서 한 시도 네 번(`episode()`, seed 2)의 return은 35.93, 34.91, 27.63, 27.26입니다.
그대로 쓰면 네 시도가 모두 위로 밀리고 가장 좋은 시도도 가장 나쁜 시도보다 32%만 더 세게 밀립니다.
다른 세 시도의 평균을 baseline으로 빼면 밀리는 힘은 +6.0, +4.6, -5.1, -5.6이 됩니다. 좋은 시도는 위로 나쁜 시도는 아래로 갑니다.

![밀어 올리는 화살표가 달린 자동차들](../assets/clip-example.mp4)

*화살표를 보세요. 처음에는 파란 화살표가 거의 같은 길이입니다. 모든 return이 크기 때문입니다. 그다음 화살표는 각 시도가 다른 시도들의 평균과 얼마나 다른지를 보여 줍니다. 초록은 위로 빨강은 아래로 갑니다.*

## 만들기

과제는 1차원 도달입니다. 조향 `a`가 자동차를 `x`에서 `x' = x + 0.2*a`로 옮기고 step마다 `3 - x'^2 - 0.01*a^2`의 reward를 줍니다.
에피소드 `i`의 시각 `t` baseline은 다른 에피소드들의 reward-to-go(step `t`부터 끝까지의 reward 합) 평균이라서 자기 행동을 보지 않습니다.

```python
G = np.array([reward_to_go(r) for _, _, r in eps])
b = (G.sum(0) - G) / (batch - 1) if baseline else np.zeros_like(G)
g += sum(score(theta, x, a) * (G[i, t] - b[i, t]) for t, (x, a) in enumerate(zip(xs, acts)))
```

`score()`는 테스트에서 유한 차분과 대조합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/03-policy-gradients -q
python3 phases/13-learning-for-robots/03-policy-gradients/code/figure.py
```

## 실제 도구로 보기

최종 return을 비교하기 전에 seed 사이의 gradient 분산부터 비교하세요.

출처: OpenAI Spinning Up, "Intro to Policy Optimization". 2026년 11월 9일에 열어 확인했습니다.
상태에만 의존하는 baseline은 기대 gradient를 바꾸지 않고 분산을 줄이며 reward-to-go는 평균이 0인 noise 항을 없앱니다.

## 결과물

`outputs/skill-policy-gradient-debug.md`는 policy gradient 실행이 불안정할 때 무엇을 잴지 정리한 목록입니다.

## 연습 문제

1. `BONUS`를 0과 10으로 두고 raw와 baseline의 차이가 어떻게 변하는지 그리세요.
2. `SIGMA`를 학습 파라미터로 바꾸고 그 `score()` 항을 유도하세요.
3. leave-one-out 평균을 전체 에피소드 평균으로 바꾸고 `batch=2`에서 편향을 검증하세요.
