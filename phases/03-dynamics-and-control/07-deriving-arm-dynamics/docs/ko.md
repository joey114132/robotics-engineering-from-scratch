# M(q)는 어디서 오는가: 팔 동역학 유도

> 팔의 관성 숫자가 어디서 오는지 알아서 로봇이 바뀌었을 때 다시 만들 수 있게 됩니다.

**유형:** 만들기   **선수 지식:** 02/03 야코비안, 03/05 Computed Torque   **시간:** 약 15분

## 쉽게 말하면

링크가 둘인 책상 위 로봇 팔이 모터가 밀지 않는 채로 자유롭게 흔들린다고 해 보세요. 아래팔의 속도에는 두 관절의 움직임이 함께 들어가요. 그래서 운동에너지를 관절별로 따로 나눌 수 없어요.

운동에너지의 합을 미분하면 관성 행렬과 관절끼리 주고받는 coupling torque가 나와요. 링크의 힘과 모멘트를 더하는 별도 계산도 같은 답을 줘야 하고 모터도 마찰도 없으면 운동에너지는 일정해요.

## 핵심 용어

- **Kinetic energy (`T`)**: 움직임의 에너지입니다. 팔에서는 `T = 1/2 qd' M qd`이고 `qd'`는 속도 목록을 옆으로 눕힌 것입니다.
- **Inertia matrix (`M`)**: 팔이 각 관절에 얼마나 무겁게 느껴지는지, 그리고 관절끼리 어떻게 엮이는지를 나타냅니다.
- **Coriolis and centripetal torques (`h`)**: `M`이 자세에 따라 변하기 때문에 생기는 속도에 따른 torque입니다.
- **Lagrange equation**: 운동에너지를 미분해서 관절 torque로 바꾸는 규칙입니다.
- **Newton-Euler**: 에너지 대신 링크마다 힘과 모멘트를 더하는 두 번째 방법입니다.
- **Positive definite**: 어떤 움직임이든 운동에너지가 양수인 성질입니다.

## 문제

팔에 더 무거운 도구를 달았더니 컨트롤러가 팔의 무게와 휘두르는 힘에 쓰는 공식이 더 이상 맞지 않습니다. 부호 하나만 잘못 적어도 컨트롤러는 엉뚱한 팔을 상쇄합니다.

## 개념

컨트롤러는 팔의 모델만큼만 좋으므로 그 모델을 다시 만들 수 있어야 합니다. 서로 독립인 두 방법이 같은 답을 줍니다. 하나는 팔의 운동에너지를 쓰고 미분합니다. 다른 하나는 link마다 힘을 더합니다.

![두 길, 하나의 토크](../assets/diagram-two-roads.png)

*하나의 torque로 가는 두 길입니다. 둘이 다르면 한쪽에 버그가 있습니다.*

팔이 각 관절에 얼마나 무겁게 느껴지는지와 관절끼리 어떻게 잡아당기는지는 에너지에서 저절로 나옵니다.

![혼자 돌 때와 함께 돌 때의 에너지](../assets/clip-example.mp4)

*각 관절이 혼자 돌 때의 에너지와 함께 돌 때의 에너지입니다. 틈이 잡아당김입니다.*

![토크의 각 항이 어디서 나오는지](../assets/diagram-energy-parts.png)

*잡아당김은 무게가 팔꿈치에 따라 변하기 때문에 생깁니다.*

마찰 없이 자유롭게 흔들리는 팔은 에너지를 유지해야 하고 이것이 틀린 부호를 잡는 날카로운 시험입니다.

![팔꿈치 각도에 따른 M과 부호가 틀린 에너지](../assets/fig-inertia-and-energy.png)

*오른쪽은 부호를 뒤집으면 에너지가 흔들리는 모습입니다.*

<details><summary>The math (optional)</summary>

`T = 1/2 qd' M(q) qd`를 풀어 쓰면 `1/2 (M11 qd1^2 + 2 M12 qd1 qd2 + M22 qd2^2)`이고 Lagrange 방정식 `tau = d/dt(dT/dqd) - dT/dq`가 `tau = M qdd + h`를 줍니다.
레슨의 팔(1 kg과 1.5 kg)이 `q = (0.3, 1.0)`에서 1 rad/s로 돌 때 관절 1만 돌리면 `T = 0.437`이므로 `M11 = 0.873`이고 관절 2만 돌리면 `T = 0.0925`이므로 `M22 = 0.185`이며
 둘을 함께 돌리면 `T = 0.836`이라서 `M12 = 0.307`입니다.
부호가 틀리면 에너지가 십분의 몇 J씩 흔들립니다.

</details>

## 만들기

세 줄이 단위 속도로 에너지에서 무게 표를 재고 torque를 만듭니다.

```python
off = T(e0 + e1) - T(e0) - T(e1)          # unit velocities
M = [[2*T(e0), off], [off, 2*T(e1)]]
tau = M @ qdd + dMdt @ qd - dTdq          # dMdt, dTdq by central differences
```

`kinetic()`이 에너지를 만들고 `lagrange_tau()`와 `newton_euler()`가 두 길입니다. 테스트는 표가 대칭 양정치인지, 두 길이 무작위 상태 20개에서 일치하는지, 부호를 뒤집으면 에너지 테스트가 실패하는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/07-deriving-arm-dynamics -q
python3 phases/03-dynamics-and-control/07-deriving-arm-dynamics/code/figure.py
```

## 실제 도구로 보기

MuJoCo는 같은 표를 `mj_fullM`으로 계산하니 `mass()`와 비교해 보세요. Craig 6장입니다.

출처: [MuJoCo API reference](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html), 2026년 11월 10일에 확인했습니다.

## 결과물

`outputs/skill-arm-dynamics-derivation-check.md`는 동역학 모델을 두 길 테스트와 에너지 테스트로 점검합니다.

## 연습 문제

1. 링크 2를 두 배 무겁게 하고 표의 어느 성분이 가장 크게 변하는지 보세요.
2. 부호 하나를 뒤집고 에너지 테스트가 실패하는 것을 보세요.
3. 링크 2의 끝에 작은 무게를 다세요.
