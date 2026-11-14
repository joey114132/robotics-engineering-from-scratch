# Particle Filter 위치 추정 (Particle Filter Localisation)

> particle을 여러 개 들고 있다가 측정으로 나쁜 것을 죽입니다. 로봇이 옮겨지는 날을 위해 엉뚱한 particle도 몇 개 남겨 둡니다.

**유형:** 만들기   **선수 지식:** 08/01 차동 구동과 Odometry   **시간:** 약 15분

## 쉽게 말하면

로버가 기둥 네 개가 서 있는 방에 있어요. 기둥은 위치를 아는 landmark이고 로버는 각 기둥까지의 거리를 재요.
로버는 자기가 있을 만한 자리를 여러 곳 짐작해 두고 측정과 거리가 잘 맞는 추측은 복제하고 안 맞는 추측은 버려요.
그다음 추측을 모두 로버가 간 만큼 옮겨요. 이 추측 무리가 particle filter예요.

이제 누가 로버를 다른 구석으로 옮겨 놓아요. 옛 추측은 모두 새 자리에서 멀어서 복제해 봐야 소용이 없어요. 방 곳곳에 무작위 추측을 조금 흩어 두면 새 측정이 찾을 거리가 생겨요.

## 문제

odometry는 오차가 점점 쌓이므로(drift) 알려진 지도 위의 로봇은 바깥 측정으로 자기 위치를 알아야 합니다.

가우시안(봉우리가 하나인 믿음) 하나로는 "두 복도 중 어느 쪽일 수도 있다"를 담을 수 없지만 particle 구름은 담을 수 있습니다. 다만 구름에도 고유한 실패가 있습니다. 자기 확신이 너무 커져서 더는 고칠 수 없게 되는 것입니다.

## 개념

![Particle filter 한 주기](../assets/diagram-pf-cycle.png)

*각 particle은 noise와 함께 움직이고 landmark까지의 거리가 측정값과 얼마나 맞는지로 점수를 받습니다. 그다음 점수에 비례해 복제되거나 버려집니다.*

particle 하나가 추측 하나이고 자세 `(x, y, heading)`입니다. weight는 얼마나 잘 맞는지를 나타냅니다. 그 particle이 예측한 거리가 측정한 거리에 가까울수록 커지고 이것이 가우시안 likelihood입니다.

참값에서 먼 구름은 weight가 너무 작아서 전부 0으로 반올림되는 underflow가 생깁니다. 그래서 weight를 로그로 두고 `exp` 전에 가장 큰 값을 뺍니다.
systematic resampling은 weight에 비례해 particle을 복제하는 방법입니다. 무작위 offset 하나에서 같은 간격의 포인터 `N`개를 뽑으므로 구름 크기가 일정합니다.

![참 자세로 모이는 particle](../assets/fig-pf-collapse.png)

*파란 점은 particle이고 주황색 별은 참 자세입니다. particle 1000개와 landmark 4개에서 구름은 몇 step 안에 별 주위로 줄어들고 40 step 뒤 오차는 0.3 m 아래입니다.*

![붕괴한 구름은 옮겨진 로봇을 찾지 못합니다](../assets/diagram-pf-kidnap.png)

*kidnap(로봇을 다른 곳으로 옮기는 것) 뒤에는 모든 particle이 잘 맞지 않고 새 자세 근처에는 particle이 하나도 없습니다.*

레슨의 kidnap 실행에서는 로버가 step 40에 `(2, 3)`에서 `(8, 7)`로 7.2 m 옮겨집니다. 어긋남은 추정값에서 로버까지의 거리입니다.
한 step 뒤 일반 filter는 3.79 m 어긋나 있고 끝까지 3.88 m 어긋납니다. 무작위 particle을 5% 섞으면 0.43 m 어긋났다가 끝에는 0.24 m 어긋납니다.

![kidnap 뒤 일반 구름과 무작위 particle을 섞은 구름](../assets/clip-example.mp4)

*주황색 로버가 들려 옮겨지는 것을 보세요. 가는 표지 하나가 추측 하나입니다. 키 큰 파랑(일반 filter)은 로버를 끝내 찾지 못하고 키 작은 초록(무작위 5%)은 로버에게 건너뜁니다. 검은 기둥은 landmark입니다.*

![kidnap 뒤 오차, random particle 유무 비교](../assets/fig-pf-kidnap.png)

*주황색(일반 filter)은 1.4 m 아래로 돌아오지 못합니다. 파란색(매 step particle 5%를 무작위로 바꿈)은 추정이 조금 더 흔들리는 대가로 회복합니다.*

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

Nav2의 AMCL은 2D 레이저 스캐너로 알려진 지도 위에서 로봇의 위치를 추정하고 반복 가능한 실행을 위한 `random_seed`가 있습니다.

구름의 퍼짐을 이 레슨과 비교해 보세요.

출처: Nav2 `nav2_amcl` README, github.com/ros-navigation/navigation2, 2026년 11월 9일에 열어 확인했습니다.

## 결과물

`outputs/skill-particle-filter-check.md`는 particle filter의 depletion과 kidnap 대응을 점검합니다.

## 연습 문제

1. `n_eff`를 시간에 따라 그리고 N/2 아래일 때만 resampling하세요.
2. 가장 큰 값 빼기를 없애고 weight가 underflow하는 step을 찾으세요.
3. landmark를 일직선에 놓고 어느 방향이 모호하게 남는지 보세요.
