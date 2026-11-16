# MDP와 Value Iteration

> 미끄러운 작은 세계의 모든 칸에서 로봇이 최선의 움직임을 계산하는 법을 배웁니다.

**유형:** 만들기   **선수 지식:** 09/05 격자 탐색   **시간:** 약 15분

## 쉽게 말하면

로버가 미끄러운 바닥을 달리는데 다섯 번에 한 번쯤은 옆으로 미끄러져요. 구덩이 옆의 지름길이 돌아가는 길보다 나쁠 수 있어요.

MDP는 행동마다 가능한 결과와 그 확률을 적어 둔 거예요. value iteration은 행동의 점수를 지금 받는 reward에 가게 될 곳의 value를 더해서 정해요. 모든 칸을 한 번 훑는 것이 sweep이에요. sweep을 반복하면 칸마다 가장 좋은 행동이 정해져요.

## 핵심 용어

- **MDP**: Markov decision process입니다. 상태와 행동과 전이 확률과 reward로 이루어집니다.
- **Value `V(s)`**: 상태 s에서 이후에 최선의 행동을 고른다고 할 때 기대되는 reward-to-go입니다.
- **Backup**: 한 상태의 value를 행동들의 reward와 다음 value로 다시 계산하는 일입니다.
- **Sweep**: 모든 상태를 한 번씩 backup하는 것입니다.
- **Discount (gamma)**: 나중 reward를 줄이는 1보다 작은 배율입니다. 빠를수록 좋기 때문입니다.
- **Greedy policy**: 각 상태에서 점수가 가장 높은 행동을 고르는 policy입니다.

## 문제

미끄러운 바닥의 로버는 가끔 옆으로 미끄러져 구덩이에 빠집니다. 칸마다 최선의 움직임을 알고 싶고 학습된 policy와 비교할 기준도 필요합니다. 작은 세계에서는 정확한 최선을 계산할 수 있습니다.

## 개념

계획하는 로봇은 확실한 작은 이득과 위험한 지름길을 저울질해야 하는데 이 방법은 그것을 숫자로 합니다.

![backup 한 번](../assets/diagram-bellman-backup.png)

*backup은 행동마다 지금의 reward에 결과 상태들의 value와 gamma를 곱한 값을 더해 점수를 내고 가장 높은 점수를 남깁니다.*

상태는 칸이고 행동은 이동입니다. `P(s' | s, a)`는 칸 s에서 행동 a로 칸 s'에 닿을 확률입니다. gamma는 여기서 0.9입니다.

![sweep 고리](../assets/diagram-value-iteration-loop.png)

*0에서 시작해 모든 상태를 backup하고 반복합니다.*

![value 퍼짐](../assets/fig-value-ripple.png)

*위쪽은 sweep마다 value가 목표에서 퍼지고 구덩이가 경로를 밀어내는 모습입니다. 아래쪽은 최종 값과의 차이가 gamma의 k제곱 이상으로 빨리 줄어드는 모습입니다(k는 sweep 횟수).*

구덩이 바로 오른쪽 칸을 봅시다. 첫 sweep이 끝난 뒤 왼쪽으로 가면 점수는 -0.8(확률 0.8로 구덩이의 -1)이고 오른쪽으로 가면 0입니다. sweep 29번 뒤에는 오른쪽이 0.64, 위나 아래가 0.43, 왼쪽이 -0.68이라서 화살표는 오른쪽을 가리킵니다.

![로버와 점수](../assets/clip-example.mp4)

*화살표는 각 이동의 점수이고 0보다 높으면 파랑 낮으면 빨강입니다.*

## 만들기

이동은 확률 0.2로 옆으로 미끄러집니다. 목표에 들어가면 +1, 구덩이에 들어가면 -1을 받습니다.

```python
def backup(model, V, gamma):
    return model.r + gamma * model.P @ V      # Q[a, s]

V = backup(model, V, gamma).max(0)            # one sweep
pi = backup(model, V, gamma).argmax(0)        # greedy policy
```

테스트는 contraction(sweep마다 차이가 줄어드는 성질), sweep 상한, 작은 격자의 policy 256개를 확인합니다. k번째 변화량은 첫 변화량의 `gamma**(k - 1)`배 이하입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/05-mdps-and-value-iteration -q
python3 phases/13-learning-for-robots/05-mdps-and-value-iteration/code/figure.py
```

## 실제 도구로 보기

이 반복은 모델 전체가 필요해서 동역학을 모르는 로봇에는 쓸 수 없습니다.

출처: Sutton과 Barto, *Reinforcement Learning: An Introduction* 4.4절을 2026년 11월 10일에 열어 봤습니다.

## 결과물

`outputs/skill-value-iteration-oracle.md`는 작은 과제의 정확한 기준 policy를 만들어 줍니다.

## 연습 문제

1. `slip`을 0.2에서 0.5로 올리세요. policy는 어디서 처음 구덩이를 피하나요?
2. `gamma`를 0.5로 놓고 sweep 횟수를 상한과 비교하세요.
3. 13/03의 policy gradient를 시작 칸의 `V`와 비교하세요.
