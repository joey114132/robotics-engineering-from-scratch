# 시뮬레이션 팔 Pick and Place

> 앞서 배운 네 가지가 하나의 작업이 됩니다. 가장 조용한 부품인 중력 feedforward를 빼면 작업 전체가 실패합니다.

**유형:** 만들기   **선수 지식:** 02/02 역기구학, 03/02 중력 보상, 09/01 궤적 프로파일   **시간:** 약 30분

## 쉽게 말하면

컵을 탁자에서 선반으로 옮기려면 팔의 각도를 고르고 갑자기 출발하지 않게 움직이며 팔 자체의 무게도 계속 받쳐야 해요.

이 시뮬레이션 팔은 IK와 quintic trajectory, gravity feedforward를 더한 PD controller를 연결해요. feedforward는 위치가 틀어지기 전부터 무게를 받칠 torque를 줘요. 이것을 빼면
controller가 충분한 torque를 만들 때까지 팔이 처져야 해요. 계획한 목적지는 그대로인데 실제 끝점은 내려놓을 자리를 빗나갈 수 있어요.

## 문제

앞의 레슨은 각자 테스트를 통과했지만 부품들이 함께 일해 본 적은 없습니다. pick-and-place는 모든 부품이 동시에 필요합니다. 하나가 틀리면 마지막에 목표를 빗나갑니다.
여기서는 평면 팔 시뮬레이션에 전체 체인을 만들고 빗나감의 원인을 읽는 법을 익힙니다.

## 개념

![pick-and-place 시스템의 구성 요소](../assets/diagram-pick-place-system.png)

*목표 위치는 관절 waypoint가 되고 waypoint는 매끄러운 경로가 됩니다. 중력 feedforward를 더한 PD 루프가 시뮬레이션 팔을 움직이고 B에서의 팁 오차가 pass와 fail을 가릅니다.*

![중단 실험 도해](../assets/diagram-pick-place-broken.png)

*feedforward가 없으면 중력 토크 전체가 잔차가 되고 position 스프링이 그 잔차를 처짐으로 바꿉니다.*

![작업이 성공하는 모습](../assets/fig-pick-place-result.png)

*팁은 A 위에서 대기하다 집고 들어 올려 B 위로 옮긴 뒤 내려놓습니다. 움직이는 동안은 계획보다 최대 9 mm 뒤처지고 B에서는 0.00 mm로 수렴합니다.*

![계획 대비 처짐](../assets/fig-pick-place-sag.png)

*feedforward가 없으면 시작 이후 팁이 계획에서 14~37 mm 벗어나고 B에서 20 mm 떨어진 곳에 놓아 검사에 실패합니다.*

## 만들기

새로 들어가는 부품은 팔 자체입니다. `M(q) a + C(q, v) + g(q) = tau`를 1 ms마다 한 걸음씩 적분합니다.

```python
q, v = step(q, v, ff * gravity(qd) + kp * (qd - q) + kd * (vd - v))
```

`ik()`가 waypoint를 주고 `reference()`가 quintic 구간을 따라 `qd, vd`를 줍니다. `ff`는 `gravity()`에서 나온 feedforward의 배율입니다.

`run()`은 pick 오차와 place 오차, 그리고 `passed`(place 오차 5 mm 미만)를 돌려줍니다. 자유 스윙 에너지 테스트가 Coriolis 항을 검증합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/16-capstones/01-arm-pick-and-place-sim -q
python3 phases/16-capstones/01-arm-pick-and-place-sim/code/main.py
```

## 실제 도구로 보기

실제 시뮬레이터는 `M`, `C`, `g`를 대신 계산해 줍니다. MuJoCo의 `qfrc_bias`는 `mj_fwdVelocity`가 계산하는 `C(qpos,qvel)`로 문서화되어 있습니다. 이 레슨의 `coriolis + gravity`와 비교해 보세요.

출처: [MuJoCo mjData 레퍼런스](https://mujoco.readthedocs.io/en/stable/APIreference/APItypes.html), 2026년 11월 9일 확인.

## 결과물

`outputs/skill-pick-place-miss-triage.md`는 B에서 빗나간 결과를 원인이 된 단계로 좁혀 줍니다.

## 연습 문제

1. feedforward 배율을 0.9로 두고 여전히 통과하는 가장 작은 `kp`를 찾으세요.
2. pick 뒤에 link 2에 0.5 kg 블록을 달고 place 오차를 관찰하세요.
3. quintic 경로를 trapezoid로 바꾸고 최대 추종 오차를 비교하세요.
