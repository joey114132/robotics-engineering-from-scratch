# 격자 탐색: Dijkstra에서 A*로 (Grid Search: Dijkstra to A*)

> A*는 약속이 붙은 Dijkstra입니다. 남은 거리를 절대 크게 잡지 않는 추측 덕분에 최적 경로에 있을 수 없는 칸을 건너뜁니다.

**유형:** 만들기   **선수 지식:** 09/03 충돌 검사   **시간:** 약 15분

## 쉽게 말하면

탐사 로봇이 벽이 있는 격자에서 깃발까지 가장 짧게 걸어가야 해요. Dijkstra는 그 칸까지 이미 쓴 걸음 수 순서로 칸을 확장해요. 확장은 그 칸의 이웃을 살펴본다는 뜻이에요. A*는 앞으로 필요한 걸음의 추측도 더해서 깃발 쪽 칸을 먼저 확장해요.

벽을 무시하고 가로로 몇 칸 세로로 몇 칸 남았는지만 세는 추측은 실제로 필요한 걸음보다 크게 말하지 않아요. 그래서 가장 짧은 길을 찾을 수 있어요. 추측을 부풀리면 가까워 보이지만 더 돌아가는 틈으로 서둘러 들어갈 수 있어요.

## 문제

planner는 격자 지도에서 경로를 눈 깜짝할 사이에 찾지만 어떻게 찾았는지는 모릅니다. 탐색을 다른 것으로 바꾸면 경로가 10칸 달라지거나 실행 단계가 열 배가 됩니다. 탐색을 직접 짜 보지 않으면 그 차이가 알고리즘 탓인지 설정 탓인지 가를 수 없습니다.

## 개념

![같은 반복에 우선순위 항 하나만 더했습니다](../assets/diagram-astar-priority.png)

*두 탐색 모두 가장 작은 우선순위의 칸을 계속 확장합니다. 우선순위만 다릅니다.*

Dijkstra는 시작점에서의 비용 `g` 순으로 칸을 확장합니다. A*는 `f = g + w * h`를 쓰고 `h`는 목표까지 비용의 추측이며 가중치 `w`가 그 추측을 키우거나 줄입니다. `w = 0`이 Dijkstra이고 `w = 1`이 A*이며 `w > 1`은 추측을 부풀립니다.

상하좌우로만 움직이는 4방향 격자에서 Manhattan distance(가로 칸 수와 세로 칸 수의 합)는 절대 과대추정하지 않으므로 A*는 Dijkstra와 같은 비용을 돌려줍니다.

한 칸 움직이면 이 거리는 많아야 1 변하고 `g`는 1 늘어나므로 `f`가 경로를 따라 줄지 않아서 같은 칸이 두 번 확장되지 않습니다.

![heuristic의 약속](../assets/diagram-astar-promise.png)

*과대추정하지 않는(admissible) `h`는 A*를 최적으로 지킵니다. `w > 1`이면 추측이 너무 클 수 있어서 경로 비용이 최적의 `w`배까지 커질 수 있습니다.*

![확장 수와 과대추정의 대가](../assets/fig-astar-expansions.png)

*같은 지도에서 세 가지 탐색입니다. 가중치 4는 칸을 덜 확장하지만 더 긴 경로를 돌려줍니다. 경로 비용은 가중치 2와 3 사이에서 26에서 36으로 뜁니다.*

예시는 trap 지도입니다. 벽 두 개가 있고 둘 다 아래쪽이 열려 있으며 첫 벽에는 위쪽 틈도 있는데 그 틈은 둘째 벽에 막혀 막다른 길이 됩니다. `w = 1`이면 탐색은 115칸을 확장하고 낮은 틈을 지나는 26걸음 길을 찾습니다.

`w = 4`이면 깃발 가까운 칸이 시작점 가까운 칸보다 우선순위가 높아서 위쪽 틈으로 파고들고 95칸을 확장한 뒤 깃발에 닿지만 길은 36걸음입니다.

![추측이 다른 탐사 로봇 두 대](../assets/clip-example.mp4)

*누가 먼저 도착하는지 보세요. 파란 쪽(`w = 4`)은 먼저 출발하지만 더 멀리 걸어서 초록 쪽(`w = 1`)이 이깁니다.*

## 만들기

```python
heap = [(w * manhattan(start, goal), 0, start)]
while heap:
    _, _, cell = heapq.heappop(heap)
    if cell in closed:
        continue
    closed.add(cell)
    for n in neighbours(cell):
        if g[cell] + 1 < g.get(n, 1e9):
            g[n] = g[cell] + 1
            heapq.heappush(heap, (g[n] + w * manhattan(n, goal), -g[n], n))
```

데모의 무작위 40x40 지도에서 같은 비용 78에 Dijkstra는 1202칸 A*는 152칸을 확장합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/05-grid-search-dijkstra-to-astar -q
python3 phases/09-motion-planning/05-grid-search-dijkstra-to-astar/code/main.py
```

## 실제 도구로 보기

같은 격자를 `w = 0`과 `w = 1`로 돌려 비용과 확장한 칸 수를 비교하세요.

출처는 Wikipedia의 A* search algorithm 문서입니다(https://en.wikipedia.org/wiki/A*_search_algorithm, 2026년 11월 10일 확인).

## 결과물

`outputs/skill-grid-search-check.md`는 planner의 heuristic, 가중치, 확장 수를 점검합니다.

## 연습 문제

1. 대각선 이동을 허용하고 admissible한 heuristic을 찾으세요.
2. `g`의 동률 처리를 반대로 바꾸고 늘어나는 칸 수를 세어 보세요.
3. trap 지도가 비용 36을 돌려주는 가장 작은 `w`를 찾으세요.
