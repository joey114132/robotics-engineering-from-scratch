# Jacobian: joint 속도, tip 속도, 힘

> joint 속도가 손의 속도를 어떻게 정하는지, 손을 미는 힘이 모터 torque로 어떻게 바뀌는지 알게 됩니다.

**유형:** 만들기   **선수 지식:** 02/01 DH 표와 URDF origin, 02/02 역기구학   **시간:** 약 15분

## 쉽게 말하면

작업대 위 로봇 팔의 어깨를 일정하게 돌리면 tip은 어깨를 중심으로 휘어 돌아요. 어깨에서 멀수록 더 빨리 움직여서 tip의 속도는 자세에 따라 달라져요.

Jacobian은 현재 자세에서 이 관계를 표로 만든 것이에요. joint 속도를 넣으면 tip 속도가 나와요. transpose는 tip을 미는 힘을 받아서 각 모터가 버티는 데 필요한 torque로 바꿔요.

## 핵심 용어

- **Jacobian (`J`)**: 현재 자세에서 joint 속도를 tip 속도로 바꾸는 행렬입니다.
- **Tip**: 손이나 도구가 달린 팔의 끝입니다.
- **Torque (`tau`)**: 비트는 힘입니다. 예를 들어 모터가 joint를 미는 힘입니다.
- **Transpose (`J^T`)**: 같은 행렬의 행과 열을 맞바꾼 것입니다.
- **Finite difference**: 입력을 아주 조금 움직여 출력이 변하는 것을 보고 기울기를 추정하는 방법입니다.
- **Dot product (`.`)**: 두 목록의 대응하는 성분끼리 곱해서 더한 값입니다.

## 문제

로봇 팔의 tip을 0.1 m/s로 직선 이동시키고 싶고 tip이 무언가를 밀 때 각 모터가 얼마나 밀어야 하는지도 알아야 합니다.

두 질문에는 같은 행렬이 필요하고 부호가 하나 틀린 Jacobian도 위치만 보는 테스트를 전부 통과합니다.

## 개념

손을 직선으로 움직이거나 탁자를 누르려면 모든 joint가 알맞은 속도와 힘을 내야 합니다.

`J`는 양방향으로 쓰입니다. `q-dot`은 joint 속도, `v`는 tip 속도, `F`는 tip 힘, `tau`는 모터 torque입니다.

![한 행렬을 두 번 쓴다](../assets/diagram-bridge.png)

*속도는 J를 통과합니다. 힘은 J의 transpose를 거꾸로 통과합니다.*

`J`의 `j`번째 열은 joint `j`만 단위 속도로 돌 때의 tip 속도입니다(Craig 5장 5.7절). tip의 일률 `F . (J q-dot)`은 joint의 일률 `tau . q-dot`과 같아야 하고 그래서 `tau = J^T F`입니다(5.9절과 5.10절).

![J를 만드는 두 방법](../assets/diagram-two-ways.png)

*손으로 미분하든 유한 차분으로 만들든 둘 다 FK에서 시작합니다. 둘이 다르면 한쪽에 bug가 있습니다.*

![step 크기와 속도 타원](../assets/fig-jacobian.png)

*왼쪽은 step 크기에 따른 오차에 최솟값이 있다는 것입니다. 오른쪽은 tip 속도 타원으로 팔이 굽으면 통통하고 거의 펴지면 가늘어집니다.*

2 kg 블록이 tip에 매달려 있으므로 `F = 2 * 9.81 = 19.6` N입니다. 쭉 펴면 tip이 0.9 m 밖에 있어서 어깨에 19.6 x 0.9 = 17.7 N m가 필요합니다. tip이 base 거의 바로 위에 있으면 `tau = J^T F`는 약 1 N m를 줍니다.

![뻗는 동안의 torque](../assets/clip-example.mp4)

*빨간 화살표는 `F`이고 주황색 막대는 `|tau|`입니다. N m당 0.03 m 높이로 그렸습니다.*

## 만들기

`J`를 만드는 두 방법입니다.

```python
J = np.array([[-l1*s1 - l2*s12, -l2*s12], [l1*c1 + l2*c12, l2*c12]])
col = (fk(q + dq, L) - fk(q - dq, L)) / (2 * eps)   # one column per joint
```

그다음 `v = J @ qd`와 `tau = J.T @ F`를 씁니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/03-jacobian-and-velocity -q
python3 phases/02-manipulator-kinematics/03-jacobian-and-velocity/code/main.py
```

## 실제 도구로 보기

physics engine과 ROS 2 라이브러리는 팔 위의 지정한 점에 대한 Jacobian을 돌려줍니다. 2링크 모델에서 이 Jacobian과 비교해 보세요.

## 결과물

`outputs/skill-jacobian-check.md`는 모든 Jacobian에 쓸 수 있는 유한 차분 검사와 일률 균형 검사입니다.

## 연습 문제

1. 단위 joint 속도에 대한 `|J q_dot|`을 `q2`에 대해 그리고 가장 작은 곳을 찾으세요.
2. link를 하나 더 넣고 `J`가 여전히 유한 차분과 맞는지 확인하세요.
3. step 1e-6이 `q`가 1000 rad 근처일 때도 통하는지 확인하세요.
