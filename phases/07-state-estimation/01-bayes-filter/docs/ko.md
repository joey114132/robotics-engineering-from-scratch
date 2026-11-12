# Bayes Filter

> 로봇은 자신이 어디 있는지 알지 못하고 각 장소의 확률만 압니다. predict는 불확실성을 더하고 update는 그것을 덜어 냅니다. 이 두 단계가 belief를 정직하게 유지합니다.

**유형:** 만들기   **선수 지식:** 01/04 Frame과 Transform 트리   **시간:** 약 15분

## 쉽게 말하면

학교 복도에서 눈을 감고 걸음을 세며 걸어 보세요. 보폭이 일정하지 않아서 어디에 있는지 여러 가능성이 남아요. 눈을 떠서 문을 보면 문이 있는 위치가 더 그럴듯해지지만 그 문이 어느 문인지는 아직
몰라요.

Bayes filter는 각 가능성을 확률로 남겨요. prediction은 불확실한 이동만큼 확률을 옮기고 퍼뜨려요. update는 관측과 맞는 위치에 더 큰 무게를 주고 확률의 합을 맞춰요.
바뀌는 것은 실제 위치가 아니라 위치에 대한 belief예요.

## 문제

로봇이 복도를 따라 굴러가면서 바퀴 회전 수로 자기 위치를 셉니다. 바퀴가 조금씩 미끄러져서 백 걸음쯤 지나면 그 숫자는 추측일 뿐입니다. 로봇은 엉뚱한 문으로 들어갑니다. 숫자를 버리는 것도 답이 아닙니다. "문"이라는 센서값 하나는 여러 장소와 맞기 때문입니다.

## 개념

![Bayes filter 한 스텝](../assets/diagram-bayes-cycle.png)

*predict는 belief를 이동량만큼 옮기고 번지게 합니다. update는 각 셀이 센서값을 얼마나 잘 설명하는지를 곱합니다.*

belief는 복도 셀마다 확률 하나를 둔 histogram입니다. predict는 이 histogram에 모션 kernel(5% 짧게, 90% 정확히, 5% 길게)을 convolution합니다.

update는 Bayes 법칙 `posterior = prior * likelihood / sum`을 씁니다.

센서값과 일치하는 셀에는 `p_hit = 0.9`를, 어긋나는 셀에는 `0.1`을 곱합니다.

![Dead reckoning과 filter의 갈림](../assets/diagram-bayes-split.png)

*센서 단계가 없으면 belief는 계속 퍼집니다. 센서 단계가 있으면 belief가 진짜 위치 근처에 남습니다.*

![센서값이 들어올수록 belief가 모입니다](../assets/fig-belief-sharpening.png)

*왼쪽은 평평한 belief에서 시작해 문을 몇 개 지나면 확률이 실제 셀에 모이는 모습입니다. 오른쪽은 entropy가 ln 20에서 약 1 nat 근처까지 내려가는 모습입니다.*

![센서가 없으면 불확실성만 커집니다](../assets/fig-dead-reckoning.png)

*왼쪽은 모션만 쓴 belief의 entropy가 계속 오르고 filter의 entropy는 일정하게 머무는 모습입니다. 오른쪽은 predict마다 분산이 `0.05 + 0.05 = 0.1` cell^2씩 늘고 시뮬레이션이 그 값과 일치하는 모습입니다.*

## 만들기

```python
def predict(bel, move, kernel=KERNEL):
    return sum(p * np.roll(bel, move + k) for k, p in zip((-1, 0, 1), kernel))

def update(bel, z, doors=DOORS, p_hit=P_HIT):
    post = bel * np.where(doors == z, p_hit, 1 - p_hit)
    return post / post.sum()
```

복도는 셀 20개짜리 고리라서 `np.roll`이 양 끝을 처리합니다. 전체 파일에는 `entropy`, `simulate`, `run`이 더 들어 있습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/07-state-estimation/01-bayes-filter -q
```

## 실제 도구로 보기

particle filter는 같은 belief를 histogram 대신 샘플로 저장하므로 2차원 지도에서도 쓸 수 있습니다. Nav2의 AMCL(Adaptive Monte Carlo Localization)은 2D 레이저 스캐너로 알려진 지도 안에서 로봇의 pose를 추정합니다.

로봇이 움직이는 동안 AMCL의 pose 분포가 퍼지는 정도를 이 레슨의 entropy와 비교해 보세요.

출처: Nav2 AMCL README, https://github.com/ros-navigation/navigation2/blob/main/nav2_amcl/README.md (2026년 11월 9일 확인).

## 결과물

`outputs/skill-bayes-filter-check.md`는 localizer에서 predict나 update 단계가 빠졌는지 검토합니다.

## 연습 문제

1. `KERNEL`을 `(0.2, 0.6, 0.2)`로 바꾸고 실행하기 전에 10스텝 뒤 분산을 예측하세요.
2. filter에 잘못된 `p_hit` 0.99를 넣고 나쁜 센서값 하나가 어떤 영향을 주는지 보세요.
3. 고리를 양 끝이 벽인 복도로 바꾸고 벽 밖으로 나간 확률이 어디로 가야 하는지 정하세요.
