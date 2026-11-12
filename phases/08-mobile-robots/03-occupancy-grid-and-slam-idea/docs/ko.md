# Occupancy Grid와 SLAM의 발상 (Occupancy Grid and the SLAM Idea)

> 지도는 그것을 그린 자세만큼만 좋으므로 mapping과 localisation은 함께 풀어야 합니다.

**유형:** 만들기   **선수 지식:** 08/01 차동 구동과 Odometry   **시간:** 약 15분

## 쉽게 말하면

교실의 여러 자리에서 지도를 그려 보세요. 의자가 보이면 그 앞의 트인 공간은 비어 있고 의자 자리에는 장애물이 있어요. 의자 뒤는 아직 몰라요. occupancy grid는 이런 단서를 작은 칸마다 모아요.

앉은 자리나 바라본 방향을 잘못 기록하면 거리를 정확히 재도 의자가 엉뚱한 칸에 그려져요. 여러 번 보면 지도가 번져요. SLAM은 지금까지 만든 지도와 관측을 맞춰 추정한 pose를 고친 뒤 새 관측을 더해요.

## 문제

레이저 로봇으로 방을 한 바퀴 돌았더니 저장된 지도에 벽이 두 겹으로 비스듬히 그려지고 옆에 유령 방이 생깁니다. 스캐너는 멀쩡했습니다. 로봇이 자기가 있지 않은 곳에 있다고 믿고 그 틀린 자리에서 스캔을 그렸을 뿐입니다.

## 개념

![레이저 빔 하나가 grid에 알려 주는 것](../assets/diagram-beam-update.png)

*빔은 지나온 cell의 log-odds를 낮추고 끝난 cell의 log-odds를 높입니다. 그 뒤에 무엇이 있는지는 말하지 않습니다.*

occupancy grid는 cell마다 숫자 `L` 하나를 저장합니다. 이 값은 "점유됨"의 log-odds입니다. 0은 모른다는 뜻입니다.

빔이 끝난 cell에는 `0.85`를 더하고 지나간 cell에서는 `0.4`를 빼고 `+-5`에서 자릅니다. 확률로 바꿀 때는 `p = 1 - 1 / (1 + exp(L))`를 씁니다. 한 스캔에서 cell은 한 번만 갱신하므로 빔이 몰려도 같은 벽을 두 번 세지 않습니다.

![참 방, 알려진 자세의 지도, drift한 지도](../assets/fig-grid-maps.png)

*왼쪽은 방입니다. 가운데는 알려진 자세에서 얻은 스캔 200개이고 회색은 상자 안쪽처럼 한 번도 못 본 곳입니다. 오른쪽은 같은 스캔을 step마다 0.003 rad씩 커지는 방향 오차로 배치한 결과입니다. 점유 cell 중 41%만 진짜입니다.*

![mapping에는 자세가, 자세에는 지도가 필요합니다](../assets/diagram-slam-loop.png)

*SLAM은 이 원을 닫습니다. 스캔을 지금까지의 지도에 맞춰 자세를 고친 다음 지도를 갱신합니다.*

![방향 오차에 따른 벽의 품질](../assets/fig-smear-curve.png)

*누적 방향 오차가 6도 아래만 되어도 점유 cell 중 진짜의 비율이 0.89에서 0.62로 떨어집니다.*

drift 모델은 매 step의 길이는 정확히 두고 방향만 step마다 조금씩 돌립니다. 이전 레슨의 윤거 오차와 같은 종류의 오차입니다.

## 만들기

```python
def update(L, pose, r, angles, max_range=8.0):
    ...  # cells crossed: L -= 0.4, cell where each beam ended: L += 0.85
    return np.clip(L, -L_MAX, L_MAX).reshape(N, N)

def drift(poses, yaw_err):
    way = np.arctan2(d[:, 1], d[:, 0]) + yaw_err * k[1:]
```

`scan()`은 숨겨진 참 세계에서 ray를 쏩니다. `build_map()`은 받은 자세에 스캔을 배치하므로 참 자세와 drift한 자세를 모두 넣을 수 있습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/03-occupancy-grid-and-slam-idea -q
python3 phases/08-mobile-robots/03-occupancy-grid-and-slam-idea/code/main.py
```

## 실제 도구로 보기

Nav2의 map server는 `nav_msgs/msg/OccupancyGrid` 지도를 읽고 저장하므로 이런 grid가 navigation stack이 읽는 형식입니다. 실제 mapping 패키지는 자세와 grid를 함께 추정합니다.

출처: Nav2 `nav2_map_server` README, github.com/ros-navigation/navigation2, 2026년 11월 9일에 열어 확인했습니다.

## 결과물

`outputs/skill-occupancy-grid-check.md`는 번지거나 두 겹이 된 지도를 진단합니다.

## 연습 문제

1. 빔 noise를 키우고 벽이 두 cell 두께가 되는 시점을 찾으세요.
2. 자유 영역 기준 `p < 0.35`를 넣고 모르는 cell 수를 세세요.
3. 마지막 스캔 하나에만 틀린 자세를 주고 피해가 얼마나 국소적인지 보세요.
