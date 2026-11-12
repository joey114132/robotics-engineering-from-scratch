# 시뮬레이션 모바일 내비게이션

> planner는 경로를 그려 주지만 로봇은 자기가 어디에 있다고 믿는 곳을 기준으로 따라갑니다. 그래서 오도메트리 추정이 어긋나면 좋은 계획도 충돌로 끝납니다.

**유형:** 만들기   **선수 지식:** 08/01 차동 구동, 08/04 Pure Pursuit, 09/03 충돌 검사   **시간:** 약 30분

## 쉽게 말하면

휴대폰이 걸음과 회전을 세어 학교 안에서 걸은 길을 그려요. 추정이 어긋나면 실제로는 다른 복도에 있는데 맞는 복도에 있다고 표시할 수 있어요. 그 표시를 기준으로 따라가면 경로가 맞아도 엉뚱한 쪽으로 가요.

이 navigation 시스템도 장애물을 피해 계획한 뒤 추정한 pose로 조향해요. 바퀴 측정의 bias가 쌓이면 추정과 실제 로봇이 멀어져요. 위치를 아는 landmark를 보면 위치와 방향을 고쳐서 같은 추종기로 다시 길을 따라갈 수
있어요.

## 문제

planner는 깨끗한 경로를 찾았고 추종기도 테스트에서는 잘 따라갔습니다. 그런데 긴 주행에서는 로봇이 목표에서 몇 미터 떨어진 벽에 붙어 있고 로봇의 화면은 여전히 경로 위라고 말합니다. 계획은 맞았고 믿음이 틀렸습니다.

## 개념

![내비게이션 시스템의 구성 요소](../assets/diagram-nav-system.png)

*격자를 로봇 반지름만큼 부풀리면 A\*가 경로를 찾습니다. shortcut이 경로를 다듬고 pure pursuit이 오도메트리 추정을 기준으로 차동 구동 로봇을 조향합니다.*

![중단 실험 도해](../assets/diagram-nav-broken.png)

*오도메트리 오차는 달릴수록 커집니다. landmark 보정이 문제가 되기 전에 오차를 되돌립니다.*

![작업이 성공하는 모습](../assets/fig-nav-result.png)

*A\*는 waypoint 77개와 21.1 m를 주고 shortcut을 거치면 waypoint 6개와 19.8 m가 됩니다. 오도메트리 오차가 작으면 로봇은 벽에 닿지 않고 목표에서 0.28 m 떨어진 곳에 도착합니다.*

![보정이 있을 때와 없을 때의 drift](../assets/fig-nav-drift.png)

*보정이 없으면 믿음이 실제 위치에서 4.7 m 벗어나고 로봇은 벽에 부딪힙니다. 1초마다 보정하면 믿음은 0.11 m 안에 머물고 목표 오차는 0.15 m입니다.*

## 만들기

로봇은 `est`를 보고 조향하고 실제 자세는 명령대로 움직입니다. 바퀴 측정값에는 속도 오차, 회전율 bias, 잡음이 들어 있습니다.

```python
vm = v * (1 + scale_err) + rng.normal(0, sigma)
wm = w + w_bias + rng.normal(0, sigma)
est = est + dt * np.array([vm * np.cos(est[2]), vm * np.sin(est[2]), wm])
```

`pose_fix()`는 로봇 좌표계에서 본 landmark 두 개로 자세를 복원합니다. heading은 두 점 사이의 방향에서, 위치는 첫 번째 landmark에서 얻습니다. 이 모델에서 벽은 beacon을 가리지 않습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/16-capstones/02-mobile-navigation-sim -q
python3 phases/16-capstones/02-mobile-navigation-sim/code/main.py
```

## 실제 도구로 보기

ROS 2 Nav2의 NavFn planner에는 `use_astar` 파라미터가 있습니다. 문서에는 "Whether to use A*. If `false`, uses Dijkstra's expansion."이라고 적혀 있습니다.
이 격자에서 두 탐색을 모두 돌려 경로를 비교해 보세요.

출처: [Nav2 NavFn](https://docs.nav2.org/rolling/configuration_and_development/configuration_guide/planners_plugins/configuring_navfn/)
2026년 11월 9일 확인.

## 결과물

`outputs/skill-nav-drift-triage.md`는 로봇이 목표를 놓쳤을 때 계획 문제와 자세 추정 문제를 가려 줍니다.

## 연습 문제

1. 주행 전반부에는 beacon을 가리고 첫 보정 전까지의 drift를 재세요.
2. 두 landmark 보정을 landmark 하나에 대한 거리 보정으로 바꾸고 무엇이 미지수로 남는지 보세요.
3. 부풀림 반지름을 0.6 m로 넓혀도 planner가 경로를 찾는지 확인하세요.
