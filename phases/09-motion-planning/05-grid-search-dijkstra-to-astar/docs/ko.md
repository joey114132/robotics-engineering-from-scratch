# 격자 탐색: Dijkstra에서 A*로 (Grid Search: Dijkstra to A*)

> 로봇이 모든 칸을 다 확인하지 않고 지도에서 가장 짧은 길을 찾는 방법을 알아봅니다.

**유형:** 만들기   **선수 지식:** 09/03 충돌 검사   **시간:** 약 15분

## 쉽게 말하면

탐사 로봇이 벽이 있는 격자에서 깃발까지 가장 짧게 걸어갈 길을 찾아요. Dijkstra는 그 칸까지 이미 쓴 걸음 수 순서로 칸을 확장해요. A*(A-star)는 앞으로 필요한 걸음의 추측도 더해서 깃발 쪽 칸을 먼저 확장해요.

실제로 필요한 걸음보다 크게 말하지 않는 추측은 가장 짧은 길을 남겨 두어요. 추측을 부풀리면 가까워 보이지만 더 돌아가는 틈으로 서둘러 들어갈 수 있어요.

## 핵심 용어

- **Dijkstra**: 그 칸까지 이미 쓴 비용 순서로 칸을 확장하는 탐색입니다.
- **A-star**: Dijkstra에 남은 비용의 추측을 더해서 목표 쪽으로 향하는 탐색입니다.
- **Expanding a cell**: 그 칸의 이웃을 살펴보고 탐색에 더하는 일입니다.
- **Heuristic (`h`)**: 목표까지 남은 비용의 추측입니다.
- **Admissible**: 실제 남은 비용보다 크게 추측하지 않는 heuristic입니다.
- **Manhattan distance**: 벽을 무시하고 가로 칸 수와 세로 칸 수를 더한 값입니다.

## 문제

배달 로봇이 격자 지도를 건넌다고 상상해 보세요. 탐색 방식을 바꾸면 경로가 10칸 달라지거나 실행 단계가 열 배가 됩니다. 탐색을 직접 짜 봐야 이유를 알 수 있습니다.

## 개념

실제 로봇은 빠르고 좋게 계획해야 하는데 추측이 둘을 맞바꾸는 손잡이입니다.

Dijkstra는 도달하는 데 싸게 든 칸부터 차례로 살피므로 사방으로 퍼집니다. A*(A-star)는 남은 거리의 추측을 더해서 목표 쪽으로 기웁니다.

![우선순위](../assets/diagram-astar-priority.png)

*같은 반복에 항 하나만 더했습니다.*

추측이 너무 크지 않으면 A*는 여전히 가장 좋은 길을 찾고 많은 칸을 건너뜁니다. 추측을 부풀리면 목표 쪽으로 서둘러 가지만 더 먼 길을 갈 수 있습니다.

![약속](../assets/diagram-astar-promise.png)

*부풀리지 않는 추측은 가장 좋은 길을 지킵니다.*

![확장 수](../assets/fig-astar-expansions.png)

*가중치가 크면 칸을 덜 확장하지만 비용이 더 듭니다.*

trap 지도에서는 위쪽 틈이 막다른 길이고 추측을 부풀린 탐색이 그리로 파고듭니다.

![탐사 로봇 두 대](../assets/clip-example.mp4)

*파란 쪽은 부풀려서 더 멀리 걷고 초록 쪽이 이깁니다.*

<details><summary>The math (optional)</summary>

Dijkstra는 시작점에서의 비용 `g` 순으로 칸을 확장합니다.
A*는 `f = g + w * h`를 쓰고 가중치 `w`가 추측 `h`를 키우거나 줄입니다.
`w = 0`이 Dijkstra이고 `w = 1`이 A*이며 `w > 1`은 추측을 부풀립니다.
상하좌우로만 움직이는 격자에서 Manhattan distance(가로 칸 수와 세로 칸 수의 합)는 과대추정하지 않으므로 A*는 Dijkstra와 같은 비용을 돌려줍니다.
한 칸 움직이면 이 거리는 많아야 1 변하고 `g`는 1 늘어나므로 `f`가 줄지 않습니다.
`w > 1`이면 경로 비용은 최적의 `w`배까지 커질 수 있습니다.
trap 지도에서 `w = 1`이면 115칸을 확장하고 낮은 틈을 지나는 26걸음 길을 찾습니다.
`w = 4`이면 위쪽 틈으로 파고들어 95칸을 확장한 뒤 깃발에 닿지만 길은 36걸음입니다(비용은 가중치 2와 3 사이에서 26에서 36으로 뜁니다). 데모의 무작위 40x40 지도에서 같은 비용 78에 Dijkstra는 1202칸 A*는 152칸을 확장합니다.

</details>

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

두 탐색의 유일한 차이는 칸마다 주는 우선순위입니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/05-grid-search-dijkstra-to-astar -q
python3 phases/09-motion-planning/05-grid-search-dijkstra-to-astar/code/main.py
```

## 실제 도구로 보기

같은 격자를 추측을 끄고 켜서 돌려 비용과 확장한 칸 수를 비교하세요.

출처는 Wikipedia의 A* search algorithm 문서입니다(https://en.wikipedia.org/wiki/A*_search_algorithm, 2026년 11월 10일 확인).

## 결과물

`outputs/skill-grid-search-check.md`는 planner의 heuristic, 가중치, 확장 수를 점검합니다.

## 연습 문제

1. 추측을 끄고 켜서 확장하는 칸 수를 비교하세요.
2. 추측을 더 크게 하고 길이 길어지는 것을 보세요.
3. 대각선 이동을 허용하고 어떤 추측이 여전히 안전한지 생각해 보세요.
