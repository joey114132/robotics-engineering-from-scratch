# 정책 경사 (Policy Gradients)

> 평균보다 높은 점수를 받은 행동 쪽으로 정책을 밀면 됩니다. 대가는 noise뿐이고 baseline이 그것을 줄입니다.

**유형:** 만들기   **선수 지식:** 13/01 시연으로부터의 모방   **시간:** 약 15분

## 문제

전문가는 없고 reward만 있어서 정책이 스스로 길을 찾아야 할 때가 있습니다. 무작위 행동을 해 보고 점수를 매긴 다음 잘된 쪽으로 움직입니다. 한 에피소드의 점수는 noise가 큰 숫자라서 같은 설정으로 학습해도 두 실행이 전혀 다르게 보일 수 있습니다.

## 개념

![REINFORCE 루프](../assets/diagram-reinforce-loop.png)

*행동을 뽑아 reward를 더합니다. 각 행동의 score에 return을 곱한 뒤 파라미터를 한 걸음 옮깁니다.*

정책은 평균이 `w*x + b`인 Gaussian입니다. 행동의 "score"는 그 행동의 log probability를 미분한 값입니다. 여기에 return을 곱해 에피소드에 걸쳐 평균하면 기대 return의 gradient 추정치가 나옵니다.

![baseline이 바꾸는 것](../assets/diagram-baseline-effect.png)

*모든 return이 크고 양수이면 뽑힌 행동이 전부 위로 밀리고 쓸모 있는 신호는 그 차이 속에 숨습니다.*

![학습 곡선과 gradient 분산](../assets/fig-reinforce-baseline.png)

*왼쪽은 seed 열 개씩입니다. baseline을 쓴 실행은 꾸준히 오르고 raw 실행은 흔들립니다. 오른쪽은 처음 상태에서 두 추정기의 평균이 같고 baseline이 분산을 약 3분의 1로 줄이는 모습입니다.*

## 만들기

과제는 1차원 도달입니다. `x' = x + 0.2*a`이고 step마다 reward는 `3 - x'^2 - 0.01*a^2`입니다. 에피소드 `i`의 시각 `t` baseline은 다른 에피소드들의 reward-to-go 평균이라서 자기 행동을 보지 않습니다.

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

라이브러리마다 `b` 자리에 넣는 것이 다르고 보통은 학습한 value function입니다. 업데이트의 꼴은 같습니다. 최종 return을 비교하기 전에 seed 사이의 gradient 분산부터 비교하세요.

출처: OpenAI Spinning Up, "Intro to Policy Optimization". 2026년 11월 9일에 열어 확인했습니다.
상태에만 의존하는 baseline은 기대 gradient를 바꾸지 않고 분산을 줄이며 reward-to-go는 평균이 0인 noise 항을 없앱니다.

## 결과물

`outputs/skill-policy-gradient-debug.md`는 policy gradient 실행이 불안정할 때 무엇을 잴지 정리한 목록입니다.

## 연습 문제

1. `BONUS`를 0과 10으로 두고 raw와 baseline의 차이가 어떻게 변하는지 그리세요.
2. `SIGMA`를 학습 파라미터로 바꾸고 그 score 항을 유도하세요.
3. leave-one-out 평균을 전체 에피소드 평균으로 바꾸고 `batch=2`에서 편향을 검증하세요.
