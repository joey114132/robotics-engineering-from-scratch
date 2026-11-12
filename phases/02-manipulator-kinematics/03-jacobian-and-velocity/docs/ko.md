# Jacobian: joint 속도, tip 속도, 힘

> 행렬 하나가 joint 속도를 tip 속도로 바꾸고 그 transpose가 tip 힘을 joint 토크로 바꿉니다.

**유형:** 만들기   **선수 지식:** 02/01 DH 표와 URDF origin, 02/02 역기구학   **시간:** 약 15분

## 쉽게 말하면

문을 열 때 경첩 가까운 곳보다 손잡이가 더 멀리 움직여요. 경첩의 회전은 같아도 경첩에서 멀기 때문이에요. 문 면에 수직으로 미는 힘도 경첩에서 멀리 가할수록 더 큰 torque를 만들어요.

Jacobian은 로봇 팔의 현재 자세에서 이런 관계를 나타내요. joint 속도를 tip 속도로 바꾸고 transpose는 주어진 tip 힘을 joint torque로 바꿔요. 속도와 힘을 같은
관계로 계산해서 양쪽의 power가 맞아요.

## 문제

tip을 0.1 m/s로 직선 이동시키고 싶은데, joint 속도는 자세에 따라 달라집니다. tip이 무언가를 밀 때 모터가 얼마나 세게 밀어야 하는지도 알아야 합니다. 두 질문은 같은 행렬이 필요하고 부호가 하나 틀린 Jacobian은 pose만 보는 테스트를 전부 통과합니다.

## 개념

![한 행렬을 두 번 쓴다](../assets/diagram-bridge.png)

*속도는 J를 통과합니다. 힘은 같은 J의 transpose를 거꾸로 통과합니다.*

`J`의 `j`번째 열은 joint `j`가 단위 속도로 움직일 때의 tip 속도입니다(Craig 5장 5.7절). 같은 행렬이 정적 관계 `tau = J^T F`를 줍니다(5.9절과 5.10절). 이유는 에너지입니다.

joint의 일률 `tau . qdot`이 tip의 일률 `F . v`와 같습니다.

![J를 만드는 두 방법](../assets/diagram-two-ways.png)

*해석적 J와 유한 차분 J는 같은 FK에서 만들어집니다. 둘이 다르면 한쪽에 bug가 있습니다.*

![step 크기와 속도 타원](../assets/fig-jacobian.png)

*왼쪽은 유한 차분 오차에 최솟값이 있고 그 아래는 반올림 잡음, 위는 곡률이 지배하는 모습입니다. 오른쪽은 단위 joint 속도가 팔이 굽었을 때 통통한 tip 속도 타원을, 거의 펴졌을 때 가는 타원을 만드는 모습입니다.*

## 만들기

FK를 손으로 미분하고 이어서 joint를 하나씩 살짝 움직여 tip이 가는 곳을 봅니다.

```python
J = np.array([[-l1*s1 - l2*s12, -l2*s12], [l1*c1 + l2*c12, l2*c12]])
col = (fk(q + dq, L) - fk(q - dq, L)) / (2 * eps)   # one column per joint
```

그다음 `v = J @ qd`와 `tau = J.T @ F`를 씁니다. 테스트 하나는 tip에 2 kg 질량을 두고 `J.T`가 중력 보상 레슨의 점질량 중력 토크를 그대로 만드는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/03-jacobian-and-velocity -q
python3 phases/02-manipulator-kinematics/03-jacobian-and-velocity/code/main.py
```

## 실제 도구로 보기

physics engine과 ROS 2 라이브러리는 팔 위의 지정한 점에 대한 Jacobian을 돌려줍니다. 2링크 모델에서 이 Jacobian과 비교하세요. 직접 쓰지 않은 Jacobian에는 같은 유한 차분 검사를 쓰세요.

## 결과물

`outputs/skill-jacobian-check.md`는 모든 Jacobian에 쓸 수 있는 유한 차분 검사와 일률 균형 검사입니다.

## 연습 문제

1. 단위 joint 속도에 대한 `|J q_dot|`을 `q2`에 대해 그리고 가장 작은 곳을 찾으세요.
2. link를 하나 더 넣고 `J`의 열 세 개가 여전히 유한 차분과 맞는지 확인하세요.
3. 유한 차분 step 1e-6이 `q`가 1000 rad 근처일 때도 괜찮은지 보이거나 안 맞는 지점을 찾으세요.
