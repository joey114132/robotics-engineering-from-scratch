# 작업 배정 (Task Allocation)

> 로봇마다 가장 가까운 작업을 차례로 고르면 빠르지만 자주 틀립니다. 최적 배정은 모든 짝을 한꺼번에 봅니다.

**유형:** 만들기   **선수 지식:** 08/01 차동 구동과 오도메트리   **시간:** 약 15분

## 문제

로봇 열 대와 물건을 집는 지점 열 곳이 있습니다. 로봇마다 가장 가까운 빈 지점을 잡게 했더니, 한 대는 근처 지점을 모두 다른 로봇이 먼저 가져가서 바닥을 가로질러 가야 합니다. 전체 이동 거리는 필요 이상으로 커졌는데 개별 선택은 하나도 틀려 보이지 않습니다.

## 개념

![탐욕 배정은 로봇 하나를 막다른 길에 몰아넣습니다](../assets/diagram-greedy-trap.png)

*탐욕 배정은 로봇을 하나씩 결정합니다. 그래서 앞에서 싸게 고른 선택이 뒤의 비싼 선택을 강요할 수 있습니다.*

![최적 배정의 아이디어](../assets/diagram-optimal-idea.png)

*Hungarian 방법은 행과 열마다 가격을 두고 합이 최소가 될 때까지 augmenting path를 따라 짝을 뒤집습니다.*

![한 배치에서 탐욕과 최적 비교](../assets/fig-assignment-map.png)

*같은 로봇 열 대와 작업 열 개입니다. 탐욕 배정은 지도를 여러 번 가로지르고 최적 배정은 대부분 짧은 이웃 짝입니다.*

![임의 문제에서의 비용 차이](../assets/fig-cost-gap.png)

*크기마다 임의 배치 300개를 보면 탐욕 배정은 N = 4에서 최적의 약 1.12배, N = 32에서 약 1.28배입니다. 더 싼 경우는 없습니다.*

비용 `C[i, j]`는 로봇 `i`에서 작업 `j`까지의 거리입니다. `C[i, perm[i]]`의 합이 최소인 순열을 찾습니다.

## 만들기

`greedy()`는 로봇을 순서대로 돌며 남은 작업 중 가장 싼 것을 고릅니다. `hungarian()`은 potential `u`, `v`를 유지하면서 모든 로봇이 짝을 찾을 때까지 교대 트리를 키웁니다.

```python
cur = C[i0 - 1, j - 1] - u[i0] - v[j]   # reduced cost of edge (robot i0, task j)
```

테스트는 N이 6 이하일 때 모든 순열을 다 돌린 brute force와 비교하고 N = 30에서는 SciPy와 비교합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/14-multi-robot-and-swarms/01-task-allocation -q
python3 phases/14-multi-robot-and-swarms/01-task-allocation/code/figure.py
```

## 실제 도구로 보기

`scipy.optimize.linear_sum_assignment`가 같은 문제를 풀고 테스트가 우리 총비용과 그 결과가 같은지 확인합니다. N = 200에서 실행 시간을 비교해 보세요.

출처: SciPy 문서의 `linear_sum_assignment`(2026년 11월 9일 확인). "find a complete assignment of workers to jobs of minimal cost"라고 적혀 있고 수정된 Jonker-Volgenant 알고리즘을 씁니다.

## 결과물

`outputs/skill-task-allocation.md`는 로봇 무리에 쓸 배정 방법을 고르고 검증하는 체크리스트입니다.

## 연습 문제

1. 비용이 0인 가짜 로봇으로 행렬을 채워 작업이 로봇보다 많은 경우를 다루세요.
2. 직선 거리 대신 격자 경로 길이를 쓰고 비용 차이 그림을 다시 그리세요.
3. 탐욕 배정이 전체에서 가장 싼 짝부터 고르게 바꾸고 차이를 다시 재세요.
