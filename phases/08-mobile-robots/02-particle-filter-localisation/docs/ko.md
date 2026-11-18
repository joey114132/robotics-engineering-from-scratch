# Particle Filter 위치 추정 (Particle Filter Localisation)

> 길을 잃었거나 번쩍 들려 옮겨진 로봇이 여러 추측을 들고 자기 위치를 찾는 방법을 알아봅니다.

**유형:** 만들기   **선수 지식:** 08/01 차동 구동과 Odometry   **시간:** 약 15분

## 쉽게 말하면

로버가 기둥 네 개가 서 있는 방에 있어요. 로버는 각 기둥까지의 거리를 재요.
로버는 자기가 있을 만한 자리를 여러 곳 짐작해 둬요. 잘 맞는 추측은 복제하고 안 맞는 추측은 버려요.
그다음 추측을 모두 로버가 간 만큼 옮겨요.

이제 누가 로버를 다른 구석으로 옮겨 놓아요. 옛 추측은 모두 새 자리에서 멀어요. 방 곳곳에 무작위 추측을 조금 흩어 두면 새 측정으로 찾아낼 수 있는 추측이 생겨요.

## 핵심 용어

- **Particle**: 로봇이 어디에 있고 어느 쪽을 보는지에 대한 추측 하나입니다.
- **Particle filter**: particle 무리를 옮기고 측정으로 점수를 매긴 뒤 resampling하는 방식입니다.
- **Landmark**: 로봇이 거리를 잴 수 있는, 위치를 아는 물체입니다. 예를 들면 기둥입니다.
- **Weight**: 이 추측이 맞다면 보였을 거리가 로봇이 실제로 잰 거리와 얼마나 가까운지를 나타내는 점수입니다.
- **Resampling**: weight가 큰 particle은 복제하고 작은 것은 버리면서 개수는 그대로 둡니다.
- **Kidnap**: 아무 말 없이 로봇을 들어서 다른 곳에 놓는 일입니다.

## 문제

복도 두 개가 똑같이 생긴 건물에 로봇이 있다고 상상해 보세요. 가장 좋은 추측 하나로는 "어느 복도든"이라고 말할 수 없습니다. 추측 무리는 두 복도를 모두 가리킬 수 있습니다. 하지만 무리가 틀린 쪽에 너무 일찍 뭉칠 수도 있습니다.

## 개념

로봇은 지도 위에서 자기 위치를 알아내고 누가 들어 옮겼을 때 다시 찾아내려고 이 방법이 필요합니다.

로봇은 자기가 있을 만한 자리를 수백 곳 짐작해 둡니다. 측정과 잘 맞는 추측은 복제하고 나머지는 버립니다. 그다음 추측을 모두 로봇이 간 만큼 옮깁니다.

![Particle filter 한 주기](../assets/diagram-pf-cycle.png)

*움직이고 점수를 매기고 복제합니다.*

![참 자세로 모이는 particle](../assets/fig-pf-collapse.png)

*추측이 별 주위로 모입니다.*

누가 로봇을 들어 옮기면 모든 추측이 참값에서 멉니다.

![kidnap 도식](../assets/diagram-pf-kidnap.png)

*옮겨진 뒤에는 근처에 추측이 없습니다.*

해결책은 매 step마다 무작위 추측을 조금 흩어 두는 것입니다. 그중 하나가 참값 근처에 떨어지면 무리가 따라갑니다.

![일반 구름과 무작위 구름](../assets/clip-example.mp4)

*무작위 추측이 없는 파랑은 끝내 못 찾습니다. 무작위 추측이 있는 초록은 로버가 있는 곳으로 단번에 건너뜁니다.*

![kidnap 뒤 오차](../assets/fig-pf-kidnap.png)

*주황색은 회복하지 못하고 파란색은 회복합니다.*

<details><summary>The math (optional)</summary>

particle은 자세 `(x, y, heading)`입니다.
예측한 거리가 측정한 거리에 가까울수록 weight가 커집니다.
참값에서 먼 구름은 weight가 전부 0으로 underflow하므로 weight를 로그로 두고 `exp` 전에 가장 큰 값을 뺍니다.
systematic resampling은 무작위 offset 하나에서 같은 간격의 포인터 `N`개를 뽑으므로 구름 크기가 일정합니다.
particle 1000개와 landmark 4개에서 40 step 뒤 오차는 0.3 m 아래입니다.
step 40에 로버가 (2, 3)에서 (8, 7)로 7.2 m 옮겨집니다.
한 step 뒤 일반 filter의 추정값은 3.79 m 떨어져 있고 끝에도 3.88 m 떨어져 있으며 1.4 m 아래로는 내려가지 못합니다.
무작위 particle을 5% 섞으면 한 step 뒤에 0.43 m이고 끝에는 0.24 m입니다.

</details>

## 만들기

```python
def log_weights(P, z, sigma, lm=LANDMARKS):
    return -0.5 * (((ranges(P, lm) - z) / sigma) ** 2).sum(axis=1)

def systematic_resample(w, rng):
    n = len(w)
    idx = np.searchsorted(np.cumsum(w), (rng.random() + np.arange(n)) / n)
    return np.minimum(idx, n - 1)
```

`pf_step()`은 predict, weight, resample, 선택적 random particle 주입을 이어 줍니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/08-mobile-robots/02-particle-filter-localisation -q
python3 phases/08-mobile-robots/02-particle-filter-localisation/code/figure.py
```

## 실제 도구로 보기

Nav2는 로봇 내비게이션 패키지입니다. 여기에는 레이저 스캔으로 알려진 지도 위의 로봇 위치를 찾는 이 방법의 완성된 구현이 들어 있습니다.

출처: Nav2 `nav2_amcl` README, github.com/ros-navigation/navigation2, 2026년 11월 9일에 열어 확인했습니다.

## 결과물

`outputs/skill-particle-filter-check.md`는 particle filter의 depletion과 kidnap 대응을 점검합니다.

## 연습 문제

1. 추측의 개수를 바꾸고 무리가 얼마나 빨리 안정되는지 보세요.
2. 무작위 추측을 끄고 로봇을 다시 옮겨 보세요.
3. 기둥을 모두 한 줄에 놓아 보세요. 어느 방향에서 추측이 안정되지 못하나요?
