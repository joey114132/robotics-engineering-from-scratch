# Domain Randomisation

> 조금씩 다른 여러 로봇에서 잘 돌도록 로봇의 controller를 튜닝하는 법을 배웁니다.

**유형:** 만들기   **선수 지식:** 12/03 System Identification   **시간:** 약 15분

## 쉽게 말하면

같은 조립 라인에서 팔이 나오지만 똑같은 팔은 하나도 없어요. 평균 팔에서 맞춘 gain은 여유가 없어서 일부 팔은 목표를 지나쳐 버려요.

domain randomisation은 조금씩 다른 시뮬레이션 팔 여러 개에 걸쳐 gain을 맞춰요. 범위가 좁으면 실제 차이를 놓쳐요. 넓으면 느리고 조심스러운 gain이 나와요.

## 핵심 용어

- **Domain randomisation**: 수치를 무작위로 바꾼 여러 시뮬레이션 로봇에 걸쳐 controller를 튜닝하는 방법입니다.
- **Nominal plant**: 평범한 평균 수치를 가진 시뮬레이션 팔입니다.
- **PD controller**: 목표에서 벗어난 만큼 밀고 움직이는 속도만큼 브레이크를 거는 controller입니다.
- **Gains**: controller가 얼마나 세게 밀고 브레이크를 걸지 정하는 두 수입니다.
- **Width (`w`)**: 각 수치를 얼마나 크게 바꿀 수 있는지를 비율로 나타낸 값입니다.
- **Settling**: 목표 가까이에 머무는 것입니다.

## 문제

controller가 시뮬레이션 팔에서는 잘 돌고 실제 팔에서는 실패합니다. 실제 팔이 조금 더 무겁고 뻑뻑하고 느리기 때문입니다. 시뮬레이터를 무작위로 흔들어 대비할 수 있지만 얼마나 넓게 흔들지가 문제입니다.

## 개념

똑같은 로봇은 없으므로 완벽한 복사본 하나에 맞춘 튜닝은 도박입니다. 대신 무게와 마찰과 지연을 무작위로 바꾼 시뮬레이션 팔 여러 개에서 튜닝합니다. 범위가 너무 좁으면 실제 차이를 놓치고 너무 넓으면 느리고 조심스러운 gain이 나옵니다.

![테스트 루프](../assets/diagram-dr-loop.png)

*모든 수치를 조금씩 바꾸고 같은 controller를 각 팔에 돌려서 몇 개가 성공하는지 셉니다.*

![폭](../assets/diagram-dr-widths.png)

*너무 좁으면 깨지기 쉽고 맞는 폭은 믿을 만하고 빠르고 너무 넓으면 느리고 지나치게 조심스럽습니다.*

![폭 훑기](../assets/fig-dr-width.png)

*왼쪽은 평균 팔에서 튜닝한 gain이 실제 팔에서 자주 실패하고 여러 팔에서 튜닝한 gain은 드물게 실패하는 모습입니다. 오른쪽은 필요 이상으로 넓게 튜닝하면 속도를 잃는 모습입니다.*

![같은 팔 12개](../assets/clip-example.mp4)

*팔이 안정되면 램프가 켜집니다. 맞는 폭으로 튜닝한 초록 팔들이 먼저 안정됩니다.*

<details><summary>The math (optional)</summary>

각 수치에 `1 +- w`를 곱합니다. PD controller가 토크 제한과 센서 지연을 가지고 관절을 1 rad 움직입니다. 0.8초까지 0.05 rad 안에 안정되고 최고점이 1.05 rad 아래이면 성공이며 실패는 2초의 비용으로 칩니다.
`tune()`은 평균 비용이 가장 낮은 `kp`, `kd` 쌍을 고릅니다. 폭 0.3은 관성 0.05를 0.035에서 0.065 사이의 값으로 바꿉니다.
이런 팔 12개에서 nominal 튜닝 gain(`kp` 4.5, `kd` 0.70)은 6개를 실패시켜 성공률이 57%로 떨어집니다. 폭 0.3에 걸쳐 맞춘 gain(`kp` 7.7, `kd` 1.35)은 99%이고 평균 0.52초에 안정됩니다.
폭 0.6에 걸쳐 맞춘 gain(`kp` 4.5, `kd` 0.88)은 12개를 모두 안정시키지만 평균 0.59초가 걸려 약 10% 느립니다.

</details>

## 만들기

`simulate()`는 여러 팔을 한꺼번에 돌립니다. `tune()`은 같은 무작위 팔들에서 모든 gain 쌍을 돌려 가장 좋은 쌍을 고릅니다.

```python
def sample(width, n, rng):
    return {k: v * (1 + width * rng.uniform(-1, 1, n)) for k, v in NOM.items()}
```

폭 0은 평균 팔을 그대로 돌려줍니다. 테스트는 팔 하나를 따로 돌린 결과가 batch 안의 같은 팔과 일치하는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/12-simulation-and-sim-to-real/04-domain-randomisation -q
python3 phases/12-simulation-and-sim-to-real/04-domain-randomisation/code/main.py
```

## 실제 도구로 보기

MuJoCo에서는 실행마다 팔의 질량과 감쇠와 마찰을 곱해서 바꿀 수 있습니다.

출처: MuJoCo 3.11.0 Python binding(2026년 11월 9일).

## 결과물

`outputs/skill-randomisation-range.md`는 randomisation 범위를 고르고 검증합니다.

## 연습 문제

1. 지연만 무작위로 바꾸세요. 어떤 수치가 가장 중요한가요?
2. 실제 폭을 0.15로 낮추세요. 가장 좋은 튜닝 폭은 얼마인가요?
3. 평균 대신 최악의 팔을 채점하세요.
