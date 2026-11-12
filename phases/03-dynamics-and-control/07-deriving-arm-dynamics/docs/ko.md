# M(q)는 어디서 오는가: 팔 동역학 유도

> 팔의 운동에너지를 한 번 쓰면 미분만으로 관성 행렬과 모든 Coriolis 항이 나옵니다.

**유형:** 만들기   **선수 지식:** 02/03 야코비안, 03/05 Computed Torque   **시간:** 약 15분

## 쉽게 말하면

책상 위에서 어깨와 팔꿈치를 함께 움직여 아래팔을 휘저어 보세요. 아래팔의 속도에는 양쪽 joint의 움직임이 함께 들어가요. kinetic energy도 joint별로 따로 계산해 끝낼 수 없고
움직임이 합쳐지는 효과가 들어가요.

arm dynamics는 link마다 kinetic energy를 더하는 데서 시작해요. 미분하면 inertia matrix와 움직임에 따른 coupling torque가 나와요. link의 힘과
moment를 더하는 별도 방법과도 torque가 같아야 해요. 외부 torque와 마찰이 없는 수평 팔은 kinetic energy를 보존해야 해요.

## 문제

레슨 03/05는 `M(q)`와 `h(q, qd)`를 주고 믿으라고 했습니다. 링크를 바꾸거나 관절을 하나 더하거나 부호 하나만 잘못 적으면 컨트롤러는 엉뚱한 팔을 상쇄합니다. 다시 만들 수 없는 공식은 새 팔에 맞게 고칠 수 없습니다.

## 개념

![에너지 길과 힘 길이 같은 토크에서 만납니다](../assets/diagram-two-roads.png)

*서로 독립인 유도 두 개입니다. 어떤 상태에서든 둘이 다르면 한쪽에 버그가 있습니다.*

수평면 팔의 운동에너지는 `T = 1/2 qd' M(q) qd`입니다. `qd`에 대해 정확히 이차식이므로 단위 속도를 넣어 `T`에서 `M`을 바로 읽을 수 있습니다. Lagrange 방정식 `tau = d/dt(dT/dqd) - dT/dq`는 `tau = M qdd + h`를 줍니다.

![토크의 각 항은 에너지 안에 출처가 있습니다](../assets/diagram-energy-parts.png)

*Coriolis 토크와 원심 토크는 `M`이 팔꿈치 각도에 따라 변하기 때문에만 생깁니다.*

일률 `qd' h`는 0일 필요가 없습니다. `1/2 qd' Mdot qd`와 같아서 자유 운동에서는 관성 변화에 따른 운동에너지 변화를 상쇄합니다.

다른 길은 Newton-Euler입니다. 바깥으로 나가며 각 링크의 가속도를 구하고 안쪽으로 돌아오며 힘과 모멘트를 더합니다. 에너지는 전혀 쓰지 않습니다.

![M은 팔꿈치에 따라 변하고 부호가 틀리면 에너지가 생깁니다](../assets/fig-inertia-and-energy.png)

*왼쪽은 링크 2의 질량 두 가지에 대한 팔꿈치 각도별 관성 성분입니다. 오른쪽은 올바른 `h`로 자유 운동을 하면 운동에너지가 일정하고 Coriolis 부호를 뒤집으면 십분의 몇 줄(J)씩 흔들리는 모습입니다.*

## 만들기

```python
off = T(e0 + e1) - T(e0) - T(e1)          # unit velocities
M = [[2*T(e0), off], [off, 2*T(e1)]]
tau = M @ qdd + dMdt @ qd - dTdq          # dMdt, dTdq by central differences
```

`kinetic()`이 링크 기하에서 `T`를 만듭니다. `lagrange_tau()`와 `newton_euler()`가 두 길입니다. 테스트는 `M`이 대칭 양정치이고 레슨 03/05의 닫힌 식과 같은지, 두 길이 서로 그리고 03/05와 무작위 상태 20개에서 일치하는지 확인합니다. `energy_drift()`는 RK4로 자유 운동을 돌리고 부호를 뒤집으면 실패해야 합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/07-deriving-arm-dynamics -q
python3 phases/03-dynamics-and-control/07-deriving-arm-dynamics/code/figure.py
```

## 실제 도구로 보기

MuJoCo는 같은 `M`을 `mj_fullM`으로 계산하고 bias force를 `data.qfrc_bias`에 저장합니다. 같은 팔을 만들어 `mass()`와 성분을 엄격한 허용 오차로 비교하세요. Craig 6장이 매니퓰레이터의 이 방정식을 유도합니다.

출처: [MuJoCo API reference](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html), 2026년 11월 10일에 확인했습니다.

## 결과물

`outputs/skill-arm-dynamics-derivation-check.md`는 손으로 유도했거나 생성한 동역학 모델을 두 길 테스트와 에너지 테스트로 점검합니다.

## 연습 문제

1. 레슨 03/02의 위치에너지 `V`를 더해 `lagrange_tau`를 확장하세요.
2. 링크 2를 두 배 무겁게 하고 `M`의 어느 성분이 가장 크게 변할지 예측하세요.
3. 링크 2의 끝에 점질량을 달고 `kinetic()`을 다시 만드세요.
