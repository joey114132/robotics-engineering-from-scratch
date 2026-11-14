# MDP와 Value Iteration

> 상태의 value는 최선의 행동이 주는 reward에 그 행동이 이어 주는 곳의 할인된 value를 더한 값이고 sweep을 반복하면 찾습니다.

**유형:** 만들기   **선수 지식:** 09/05 격자 탐색   **시간:** 약 15분

## 쉽게 말하면

로버가 미끄러운 바닥을 달리는데 다섯 번에 한 번쯤은 옆으로 미끄러져요. 그러면 구덩이 옆의 지름길이 돌아가는 길보다 나쁠 수 있어요. 한 번만 미끄러져도 로버가 구덩이에 빠지기 때문이에요.

MDP(Markov decision process)는 행동마다 가능한 결과와 그 확률을 적어 둔 거예요. value iteration은 행동의 점수를 지금 받는 reward에 가게 될 곳의 나중 value를 더해서 정하고 확률로 평균해요.
모든 칸을 한 번 훑는 것이 sweep이에요. sweep을 반복하면 목표의 좋은 소식과 구덩이의 나쁜 소식이 퍼져서 칸마다 가장 좋은 행동이 정해져요.

## 문제

13/03에서는 policy가 표본으로 얻은 return만 보고 길을 찾았고 그것이 최선에 가까운지는 믿는 수밖에 없었습니다. 작은 문제에서는 알 수 있습니다.
최선의 답을 정확히 계산할 수 있고 그러면 학습된 policy마다 비교할 기준이 생깁니다.

## 개념

![한 상태의 backup 한 번](../assets/diagram-bellman-backup.png)

*번호를 따라가 보세요. backup은 칸 하나의 value를 다시 계산하는 일입니다. 행동마다 지금의 reward에 결과 상태들의 value와 gamma를 곱한 값을 더해 점수를 내고 가장 높은 점수를 남깁니다.*

MDP는 상태(칸)와 행동(이동)과 전이 확률 `P(s' | s, a)`(칸 s에서 행동 a로 칸 s'에 닿을 확률)과 reward로 이루어집니다. value `V(s)`는 13/03의 reward-to-go를 확률로 평균한 값이고 이후에 최선의 행동을 고른다고 가정합니다.
할인율 gamma(여기서는 0.9)는 한 걸음 뒤의 reward를 그만큼 줄여서 셉니다. 빠를수록 좋기 때문입니다.

![sweep 반복 고리](../assets/diagram-value-iteration-loop.png)

*0에서 시작해 모든 상태를 backup하고 반복합니다. 값이 더는 변하지 않으면 칸마다 점수가 가장 높은 행동을 고르는 greedy policy가 나옵니다.*

![목표에서 퍼져 나가는 value](../assets/fig-value-ripple.png)

*위쪽은 sweep마다 value가 목표에서 더 멀리 퍼지고 구덩이가 경로를 밀어내는 모습입니다. 아래쪽은 현재 값과 최종 값의 차이가 gamma의 k제곱 이상으로 빨리 줄어드는 모습입니다(k는 sweep 횟수).*

구덩이 바로 오른쪽 칸을 봅시다. 첫 sweep이 끝난 뒤 모든 value가 아직 0일 때 왼쪽으로 가면 점수는 -0.8(확률 0.8로 구덩이의 -1)이고 오른쪽으로 가면 0입니다.
sweep 29번 뒤(`value_iteration()`)에는 오른쪽이 0.64, 위나 아래가 0.43, 왼쪽이 -0.68입니다. 이 칸의 value는 0.64이고 화살표는 오른쪽을 가리킵니다.

![점수 화살표 네 개를 단 로버](../assets/clip-example.mp4)

*화살표를 보세요. 각 이동의 점수이고 0보다 높으면 파랑 낮으면 빨강입니다. 가장 높은 화살표가 초록이 되면 로버가 그쪽으로 갑니다.*

## 만들기

세계는 격자이고 이동이 확률 0.2로 옆으로 미끄러집니다. 목표에 들어가면 +1, 구덩이에 들어가면 -1을 받습니다.

```python
def backup(model, V, gamma):
    return model.r + gamma * model.P @ V      # Q[a, s]

V = backup(model, V, gamma).max(0)            # one sweep
pi = backup(model, V, gamma).argmax(0)        # greedy policy
```

테스트는 contraction(수축), sweep 상한, 작은 격자의 policy 256개를 확인합니다. `0 < gamma < 1`에서 `delta1 = max(abs(V1 - V0))`로 둡니다.

k번째 변화량은 `gamma**(k - 1) * delta1` 이하입니다. 이 상한이 `tol`보다 엄격히 작아지는 첫 k가 sweep 횟수의 상한입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/05-mdps-and-value-iteration -q
python3 phases/13-learning-for-robots/05-mdps-and-value-iteration/code/figure.py
```

## 실제 도구로 보기

이 반복은 모델 전체가 필요해서 동역학을 모르는 로봇에는 쓸 수 없습니다. 그 경우를 위해 policy gradient가 있습니다.

출처: Sutton과 Barto, *Reinforcement Learning: An Introduction* 2판 초안 4.4절을 2026년 11월 10일에 열어 봤습니다.
이 글은 value iteration을 한 번의 sweep에서 멈춘 policy evaluation과 개선을 합친 것으로 설명합니다.

## 결과물

`outputs/skill-value-iteration-oracle.md`는 작은 시뮬레이션 과제를 정확한 기준 policy로 바꿔 줍니다.

## 연습 문제

1. `slip`을 0.2에서 0.5로 올리고 policy가 처음으로 구덩이를 피하는 지점을 찾으세요.
2. `gamma`를 0.5로 놓고 sweep 횟수를 상한과 비교하세요.
3. 이 격자에서 13/03의 policy gradient를 돌려 return을 시작 칸의 `V`와 비교하세요.
