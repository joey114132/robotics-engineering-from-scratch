# 행동 복제의 함정 (Behaviour Cloning Pitfalls)

> 복제한 정책은 전문가가 달린 곳에서는 정확하지만 한 걸음 뒤에는 틀립니다. 자기가 낸 실수 때문에 전문가가 가 본 적 없는 곳에 서게 되기 때문입니다.

**유형:** 만들기   **선수 지식:** 13/01 시연으로부터의 모방   **시간:** 약 15분

## 문제

복제한 정책이 따로 떼어 둔 시연 데이터에서는 점수가 좋은데 로봇에서는 경로를 벗어나 실패합니다. 학습 loss는 정책이 스스로 만드는 상태를 한 번도 재지 않았습니다. 작은 오차가 생길 때마다 정책은 데이터에서 조금씩 멀어집니다.

## 개념

![오차가 오차를 키웁니다](../assets/diagram-drift-loop.png)

*행동 하나가 틀리면 다음 관측이 시연 밖으로 밀려납니다. 거기서는 정책이 더 나쁘고 다음 오차는 더 커집니다.*

명령 속도에 noise를 더해서 미끄러짐과 지연을 흉내 냅니다. 깨끗한 시연이 네 번뿐이면 학습자는 몇 step 안에 시연된 상태를 벗어납니다. 그러면 행동 오차가 올라가 높은 채로 머뭅니다.

![DAgger 루프](../assets/diagram-dagger-loop.png)

*학습자가 달리면 전문가가 그 학습자가 실제로 지나간 상태에 라벨을 붙입니다. 그 짝이 데이터에 합쳐집니다.*

![호라이즌에 따른 오차와 라운드에 따른 성공률](../assets/fig-cloning-drift.png)

*왼쪽은 단순 복제의 오차가 처음 60 step 동안 약 7배로 오르는 반면 DAgger를 네 라운드 거친 정책은 0 근처에 머무는 모습입니다. 오른쪽은 noise 아래의 성공률이 두 라운드쯤에 전문가 수준까지 오르는 모습입니다.*

## 만들기

`rounds=0`이면 `dagger()`는 단순 복제입니다. 라운드마다 라벨 붙은 복구 상태가 추가됩니다.

```python
for _ in range(rounds):
    V = np.vstack([rollout(pol, x0, rng)[:-1] for x0 in starts(rng, 5)])
    X, A = np.vstack([X, V]), np.vstack([A, [expert(x) for x in V]])
    pol = fit_knn(X, A)
```

라벨은 항상 `expert(x)`에서 오고 학습자에게서 오지 않습니다. `drift_curves()`는 매 스텝의 행동 오차와 가장 가까운 데이터 상태까지의 거리를 돌려줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/13-learning-for-robots/02-behaviour-cloning-pitfalls -q
python3 phases/13-learning-for-robots/02-behaviour-cloning-pitfalls/code/figure.py
```

## 실제 도구로 보기

로봇이 달리는 동안 전문가를 쓸 수 없는 경우가 많습니다. 그래서 DAgger는 사람이나 planner가 나중에 상태에 라벨을 붙여 줘야 합니다. 더 싼 방법으로는 복구 동작을 일부러 녹화할 수 있습니다. 어느 쪽이든 오차는 따로 둔 시연이 아니라 학습자의 롤아웃에서 잽니다.

출처: Ross, Gordon and Bagnell, arXiv:1011.0686. 2026년 11월 9일에 열어 확인했습니다.
본문에 따르면 supervised 학습자는 자기가 만든 상태 분포에서 T 스텝 동안 최대 T²번 틀릴 수 있고 DAgger는 반복마다 데이터셋을 합쳐 갑니다.

## 결과물

`outputs/skill-cloning-drift-audit.md`는 복제 정책에서 누적되는 오차를 찾는 절차입니다.

## 연습 문제

1. 단순 복제의 `drift_curves`에서 `dist`를 그리고 학습자가 데이터를 벗어나는 시점을 말하세요.
2. `NOISE`를 절반으로 줄이고 전문가와 맞먹는 최소 라운드 수를 찾으세요.
3. 논문의 `beta`처럼 전문가 비중이 라운드마다 줄어드는 혼합 정책으로 롤아웃하고 비교하세요.
