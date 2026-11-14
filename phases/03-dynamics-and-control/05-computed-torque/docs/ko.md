# Computed Torque

> 팔의 운동 방정식을 안다면 그 식으로 팔을 상쇄하고 남은 것만 제어합니다.

**유형:** 만들기   **선수 지식:** 03/03 임피던스 제어, 03/04 PID와 튜닝   **시간:** 약 15분

## 쉽게 말하면

테이블 위를 쓸고 지나가는 링크가 둘인 팔을 떠올려 보세요. 팔꿈치를 펴면 손이 어깨에서 멀어져서 팔꿈치를 굽혔을 때보다 같은 swing에 어깨 torque가 더 많이 들어요. 빠르게 휘두르면 링크가 서로를 잡아당기기도 해요.

computed torque는 팔의 방정식으로 이런 영향이 요구하는 torque를 계산해서 미리 넣어 줘요. 남는 오차는 작은 보정이 맡아요. 모델의 질량이 틀리면 그 torque의 일부가 빠져요.

## 문제

관절별 PD 컨트롤러(오차만큼 밀고 속도만큼 브레이크를 겁니다)는 느린 움직임을 잘 따라갑니다. 같은 움직임을 네 배 빠르게 하면 팔이 뒤처지고 흔들립니다. 느릴 때는 작았던 관성 토크와 결합 토크가 이제 지배하기 때문입니다.

## 개념

![빠르면 PD가 실패합니다](../assets/diagram-pd-blind-spot.png)

*팔꿈치 각도가 관성을 바꾸고 빠른 swing은 Coriolis 토크(링크의 회전이 서로를 잡아당기는 힘)를 더합니다. PD는 둘 다 갑작스러운 외란으로 봅니다.*

수평면의 2링크 팔 동역학은 `tau = M(q) qdd + h(q, qd)`입니다(`q`는 관절 각도이고 `qd`와 `qdd`는 속도와 가속도입니다). `M`은 관성 행렬(팔이 각 관절에 얼마나 무겁게 느껴지는지)이고 `h`는 Coriolis 토크와 centripetal 토크입니다. 중력(레슨 03/02)은 뺍니다.

computed torque는 `tau = M(q) a + h(q, qd)`를 고르고 `a = qdd_d + kd ed + kp e`로 둡니다. 여기서 `qdd_d`는 계획한 가속도이고 `e`와 `ed`는 위치 오차와 속도 오차입니다. `tau = M qdd + h`이기도 하므로 모델이 팔을 상쇄해서 `qdd = a`가 되고 오차는 `e'' + kd e' + kp e = 0`을 따릅니다. 스프링과 damper가 0으로 가라앉는 식입니다.

![두 층으로 된 computed torque](../assets/diagram-computed-torque.png)

*안쪽 층은 모델이고 바깥쪽 층은 오차에 건 단순한 PD입니다.*

![관성과 PD가 무시하는 토크](../assets/fig-model-terms.png)

*왼쪽은 관절 1의 관성이 팔꿈치에 따라 약 네 배 달라지는 모습입니다. 오른쪽은 reference를 따라 움직일 때 관성 토크와 Coriolis 토크가 크다는 것을 보여 줍니다.*

![추종 오차](../assets/fig-tracking-error.png)

*두 컨트롤러를 같은 `omega = 20`으로 맞추고 1초 swing을 돌렸습니다. 모델이 정확하면 computed torque는 PD보다 오차가 약 300배 작습니다.*

예: 실제 팔의 `m1`이 모델보다 20% 크고 `m2`는 20% 작습니다. PD는 오차가 최대 0.19 rad까지 커집니다. 틀린 모델의 computed torque는 최대 0.038 rad로 약 5배 작습니다.

![틀린 질량](../assets/clip-example.mp4)

*반투명 기준 팔(계획한 경로)에 대한 팔끝의 위치를 보세요. 파란 팔(PD)은 최대 0.19 rad 뒤처지고 초록 팔(computed torque)은 질량이 틀려도 가까이 붙어 갑니다. 3분의 1 속도입니다.*

## 만들기

```python
M = mass(q, model)                      # 2x2, depends on the elbow angle
a = qdd_d + 2*w*(qd_d - qd) + w*w*(q_d - q)
tau = M @ a + coriolis(q, qd, model)    # Coriolis and centripetal terms
```

`main.py`에 `M`과 `h`의 전체 항이 있습니다. 테스트는 `M`을 Cartesian 속도로 계산한 운동에너지와 비교하고 `M qdd + h`를 수치 Lagrangian과 비교합니다. 자유 운동에서 운동에너지가 보존되는지도 확인하며 이것이 Coriolis 부호를 검사합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/03-dynamics-and-control/05-computed-torque -q
python3 phases/03-dynamics-and-control/05-computed-torque/code/figure.py
```

## 실제 도구로 보기

MuJoCo의 `mj_inverse`는 주어진 `qacc`에 필요한 토크 `qfrc_inverse`를 돌려줍니다. 테스트 하나가 같은 팔을 MuJoCo로 만들어 `inverse_dynamics`와 1e-9 안에서 비교합니다. 비선형 제어 법칙은 Craig 10장에 있습니다.

출처: [MuJoCo API reference](https://mujoco.readthedocs.io/en/stable/APIreference/APIfunctions.html), 2026년 11월 9일에 확인했습니다.

## 결과물

`outputs/skill-computed-torque-check.md`는 모델 기반 컨트롤러를 모델 오차와 샘플링 관점에서 점검합니다.

## 연습 문제

1. 레슨 03/02의 중력을 `h`에 더하고 위치 에너지를 포함해 에너지 테스트가 계속 성립하게 하세요.
2. 질량 하나를 0.5배에서 1.5배까지 바꾸며 최대 오차를 그리세요.
3. computed torque를 1 kHz 대신 100 Hz로 돌리고 오차 하한이 어디로 움직이는지 보세요.
