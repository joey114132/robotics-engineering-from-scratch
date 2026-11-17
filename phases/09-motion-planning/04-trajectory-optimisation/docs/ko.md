# 궤적 최적화 (Trajectory Optimisation)

> 지그재그 경로를 장애물에 다시 부딪히지 않게 부드럽게 펴서 로봇이 따라갈 수 있게 만드는 방법을 알아봅니다.

**유형:** 만들기   **선수 지식:** 09/03 충돌 검사   **시간:** 약 15분

## 쉽게 말하면

탐사 로봇의 경로는 출발점과 깃발에 고정된 waypoint 사슬이에요. 핀 두 개 사이에 당겨 둔 고무줄 앞을 장애물이 막고 있는 것과 같아요.
고무줄은 각 waypoint를 양옆 이웃을 잇는 직선 쪽으로 당겨요. 장애물은 가까이 온 waypoint를 바깥으로 밀어내요.

경로는 당기는 힘과 미는 힘이 균형을 이루는 곳에 멈춰요. 조금씩 옮기면 경로가 얼마나 나쁜지 나타내는 cost가 줄어요. 너무 크게 옮기면 오히려 늘어요.

## 핵심 용어

- **Waypoint**: 경로 위의 점 하나입니다. 경로는 이 점들의 사슬입니다.
- **Cost**: 경로가 얼마나 나쁜지 나타내는 숫자 하나입니다. 낮을수록 좋습니다.
- **Gradient**: 비용이 가장 빨리 커지는 방향입니다. 반대쪽으로 한 걸음 가면 비용이 줄어듭니다.
- **Gradient descent**: gradient의 반대쪽으로 작은 걸음을 되풀이하는 방법입니다.
- **Penalty**: waypoint가 장애물에 너무 가까워지면 더해지는 추가 비용입니다.
- **Clearance**: 경로와 장애물 사이에 남겨 두는 여유 거리입니다.

## 문제

로봇 팔이 모든 장애물을 피하지만 지그재그인 경로를 따라간다고 상상해 보세요. 시간이 낭비되고 팔이 흔들립니다. 손으로 펴면 경로가 다시 장애물 안으로 들어갑니다.

## 개념

실제 로봇은 부드러운 경로에서 시간과 마모를 아낍니다.

경로를 양 끝이 고정된 고무줄이라고 생각해 보세요. 고무줄은 각 점을 이웃 쪽으로 당기고 장애물은 가까이 온 점을 밀어냅니다.

![비용 루프](../assets/diagram-cost-loop.png)

*부드러움과 장애물이 각 점을 밀고 당깁니다.*

경로는 당기는 힘과 미는 힘이 균형을 이루는 곳에 멈추고 점을 조금씩 옮겨서 거기에 이릅니다. 너무 크게 옮기면 지나칩니다.

![두 힘](../assets/diagram-two-forces.png)

*당김과 밂은 멈춘 경로에서 균형을 이룹니다.*

![당김과 밂](../assets/clip-example.mp4)

*빨간 화살표는 당기는 힘과 미는 힘입니다. 미는 힘은 아주 크게 시작해서 줄어듭니다.*

![전후 비교](../assets/fig-before-after.png)

*전에는 두 장애물을 지나가고 후에는 돌아갑니다.*

<details><summary>The math (optional)</summary>

부드러움 cost는 이웃 점 사이 걸음의 제곱합의 절반이고 waypoint에서의 gradient는 `2 x_i - x_{i-1} - x_{i+1}`이므로 그 반대로 가면 점이 이웃을 잇는 직선 쪽으로 당겨집니다.
장애물 penalty는 waypoint가 중심에서 `r + margin`보다 가까우면 `w (r + margin - d)^2`이고 그렇지 않으면 0입니다(`w` = 8). 크기 `lr` = 0.04인 걸음을 되풀이하고 걸음이 너무 크면 cost가 오릅니다.
예: (0, 0)과 (10, 0)에 핀이 있고 그 사이의 waypoint가 (5, 0.2)에서 시작하며 장애물은 (5, 0)에 반지름 1이고 `margin = 0.4`입니다.
부드러움은 0.4로 아래로 당기고 장애물은 19.2로 위로 밉니다.
8걸음 뒤에는 (5, 1.24)에 멈추고 두 힘은 모두 2.49이며 장애물에서 0.24 떨어져 있습니다.
penalty는 waypoint에만 주므로 두 waypoint 사이의 선분은 여전히 장애물에 걸릴 수 있습니다.
장애물이 없으면 경로는 간격이 고른 직선이 됩니다.

</details>

## 만들기

```python
g[1:-1] = ws * (2*X[1:-1] - X[:-2] - X[2:])
g[1:-1] -= 2 * wo * np.maximum(0, r + margin - d) * v / d
X -= lr * g
```

끝점은 gradient가 0이라서 움직이지 않습니다. 테스트가 각 점을 살짝 움직여 변화를 재서 gradient를 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/09-motion-planning/04-trajectory-optimisation -q
python3 phases/09-motion-planning/04-trajectory-optimisation/code/main.py
```

## 실제 도구로 보기

완성된 SciPy 최적화 함수는 같은 비용과 gradient를 받습니다. 마지막 테스트가 일반 descent 4000걸음보다 나쁘지 않은 비용에 도달하는지 확인합니다.

출처는 [CHOMP, Ratliff 외 2009](https://www.ri.cmu.edu/pub_files/2009/5/icra09-chomp.pdf)이고 2026년 11월 9일에 열람했습니다.

## 결과물

`outputs/skill-path-smoothing-check.md`는 다듬은 경로의 clearance, 끝점, 걸음 크기를 점검합니다.

## 연습 문제

1. 장애물을 경로에 가까이 옮기고 경로가 비켜 휘는 것을 보세요.
2. 걸음을 키워서 점수가 나빠지는 때를 보세요.
3. 09/03처럼 점들 사이의 곧은 구간에 충돌이 없는지 검사해 보세요.
