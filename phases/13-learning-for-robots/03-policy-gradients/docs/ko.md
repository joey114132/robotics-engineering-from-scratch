# 정책 경사 (Policy Gradients)

> 가르쳐 주는 사람 없이 점수만으로 로봇이 나아지는 방법과 학습이 흔들리는 이유를 배웁니다.

**유형:** 만들기   **선수 지식:** 13/01 시연으로부터의 모방   **시간:** 약 15분

## 쉽게 말하면

장난감 자동차가 선 위에 멈춰야 하는데 방법은 아무도 알려 주지 않아요. 시도마다 선에 가까이 멈출수록 높은 점수를 줘요. 점수가 높았던 시도의 움직임이 더 자주 나오도록 조향 규칙을 바꿔요.

## 핵심 용어

- **Reward-to-go**: 지금부터 시도가 끝날 때까지 모은 점수입니다.
- **Return**: 시도(episode) 하나에서 받은 점수의 합입니다.
- **Policy gradient**: 평균보다 높은 점수를 받은 움직임 쪽으로 policy를 미는 방법입니다.
- **Baseline**: 좋은 움직임이 두드러지도록 점수에서 빼는 평균입니다.
- **Variance**: 결과가 실행마다 튀는 정도입니다.

## 문제

장난감 자동차가 선 위에 멈춰야 하지만 아무도 방법을 보여 줄 수 없습니다. 시도마다 점수만 줄 수 있습니다. 무작위 시도는 점수가 들쭉날쭉해서 같은 설정으로 학습해도 두 실행이 전혀 다르게 보일 수 있습니다.

## 개념

전문가가 없을 때 로봇이 배울 수 있는 길은 점수를 받으며 시행착오를 겪는 것뿐입니다. 자동차는 무작위로 움직여 보고 점수가 좋았던 움직임 쪽으로 조향을 밉니다. 모든 시도가 높은 점수를 받으면 모든 움직임이 위로 밀려서 진짜 차이가 묻힙니다. 다른 시도들의 평균 점수를 빼면 해결됩니다.

![REINFORCE 루프](../assets/diagram-reinforce-loop.png)

*무작위로 움직여 보고 점수를 더한 뒤 점수가 좋았던 쪽으로 조향을 밉니다.*

![baseline](../assets/diagram-baseline-effect.png)

*모든 점수가 크면 모든 움직임이 위로 밀립니다. baseline은 차이만 남깁니다.*

![곡선](../assets/fig-reinforce-baseline.png)

*왼쪽은 baseline을 쓰면 학습이 꾸준히 오르고 쓰지 않으면 흔들리는 모습입니다. 오른쪽은 baseline이 미는 힘을 훨씬 안정시키는 모습입니다.*

![화살표가 달린 자동차들](../assets/clip-example.mp4)

*파란 화살표는 모두 거의 같은 길이입니다. 평균을 빼면 초록 화살표는 위로 밀고 빨간 화살표는 아래로 밉니다.*

<details><summary>The math (optional)</summary>

policy는 Gaussian(종 모양으로 무작위하게 고르는 분포)이고 자동차는 `w*x + b` 근처로 조향하면서 탐험 noise를 더합니다.
행동마다 미는 방향(`score()`)에 return을 곱해 평균하면 기대 return의 gradient를 추정합니다.
같은 출발점에서 시도 네 번의 return은 35.93, 34.91, 27.63, 27.26이라서 네 시도가 모두 위로 밀리고 가장 좋은 시도도 가장 나쁜 시도보다 32%만 더 세게 밀립니다.
다른 세 시도의 평균을 baseline으로 빼면 밀리는 힘은 +6.0, +4.6, -5.1, -5.6이 됩니다. baseline 계산에 그 시도 자신의 움직임이 들어가지 않으므로 그쪽으로 치우치지 않습니다. seed 열 개에서 퍼짐을 약 3분의 1로 줄입니다.
과제는 1차원 도달이고 `x' = x + 0.2*a`이며 step마다 `3 - x'^2 - 0.01*a^2`의 reward를 줍니다. 클립의 화살표는 4배 길게 그렸습니다.

</details>

## 만들기

자동차는 직선 위에서 목표를 향해 조향합니다. 시도마다의 baseline은 다른 시도들의 reward-to-go 평균입니다.

```python
G = np.array([reward_to_go(r) for _, _, r in eps])
b = (G.sum(0) - G) / (batch - 1) if baseline else np.zeros_like(G)
g += sum(score(theta, x, a) * (G[i, t] - b[i, t]) for t, (x, a) in enumerate(zip(xs, acts)))
```

테스트는 미는 방향을 느리고 단순한 계산과 대조합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/03-policy-gradients -q
python3 phases/13-learning-for-robots/03-policy-gradients/code/figure.py
```

## 실제 도구로 보기

최종 점수를 비교하기 전에 미는 힘이 실행마다 얼마나 튀는지부터 비교하세요.

출처: OpenAI Spinning Up, "Intro to Policy Optimization". 2026년 11월 9일에 열어 확인했습니다.

## 결과물

`outputs/skill-policy-gradient-debug.md`는 실행이 불안정할 때 무엇을 잴지 정리한 목록입니다.

## 연습 문제

1. 모든 시도의 점수에 똑같이 큰 보너스를 더해 보세요. 두 방법의 차이가 어떻게 변하나요?
2. 한 번 더 돌려 보세요. baseline이 여전히 도움이 되나요?
3. 모든 시도의 평균을 baseline으로 쓰세요. 시도가 둘뿐일 때 편향되나요(잘못된 쪽으로 치우치나요)?
