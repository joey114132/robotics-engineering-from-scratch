# Singularity와 damped least squares

> 거의 펴진 팔에서 관절이 왜 미친 듯이 도는지, 그리고 그것을 가라앉히는 작은 요령을 알게 됩니다.

**유형:** 만들기   **선수 지식:** 02/03 Jacobian   **시간:** 약 15분

## 쉽게 말하면

작업대 위 로봇 팔이 팔꿈치를 펴면서 손을 바깥으로 보내요. 거의 다 편 상태에서는 link들이 일직선에 가까워져서 팔꿈치를 돌리면 손이 주로 옆으로 움직여요. 팔꿈치는 점점 더 빨리 돌아야 하고 완전히 펴면 어떤 회전도 손을 바깥으로 보내지 못해요.

이 자세가 singularity이고 여기서 일반 Jacobian 역행렬은 엄청나게 큰 joint 속도를 요구해요. damped least squares는 작은 속도 오차를 받아들여서 그 속도에 상한을 둬요.

## 핵심 용어

- **Singularity**: 완전히 곧게 뻗은 팔처럼 tip이 움직일 수 있는 방향 하나를 잃은 자세입니다.
- **Jacobian inverse**: 원하는 tip 속도를 다시 joint 속도로 바꾸는 행렬입니다.
- **Determinant (`det J`)**: 행렬에서 계산하는 숫자 하나로 행렬이 방향을 잃으면 0으로 떨어집니다.
- **Manipulability**: tip이 얼마나 자유롭게 움직일 수 있는지 나타내는 점수입니다.
- **Singular value**: 행렬이 한 방향을 얼마나 늘리는지입니다. 작으면 그 방향이 거의 사라진 것입니다.
- **Damped least squares**: 작은 오차(`lam`)를 받아들여서 joint 속도를 제한하는 역행렬입니다.

## 문제

로봇의 손을 바깥쪽으로 곧게 0.1 m/s로 움직이라고 명령합니다. 팔이 거의 뻗으면 controller가 elbow에 초당 100 라디안을 요구하고 drive가 한계에 걸려 tip이 경로를 벗어납니다.

## 개념

실제 팔은 한 방향의 움직임이 사라지는 자세 근처를 지나가고 controller는 그것을 견뎌 내야 합니다.

![일이 벌어지는 순서](../assets/diagram-chain.png)

*elbow 각이 줄면 `det J`가 줄어들고 역행렬은 엄청난 속도를 요구합니다.*

이 팔은 `det J = L1 L2 sin q2`이므로 완전히 뻗거나 완전히 접히면 singular입니다(Craig 5장 5.8절). 그러면 어떤 joint 속도로도 tip을 팔 방향으로 움직일 수 없습니다.

manipulability `sqrt(det(J J^T))`는 elbow가 직각일 때 가장 큽니다.

`J`의 각 열은 joint 하나가 돌 때 tip이 가는 방향입니다. `q2 = 1.4` rad에서는 `det J = 0.5 * 0.4 * sin 1.4 = 0.20`이고 `q2 = 0`에서는 두 열이 평행이 되어 `det J = 0`입니다.

![합쳐지는 두 화살표](../assets/clip-example.mp4)

*`J`의 두 열로 어깨(주황색)와 팔꿈치(진한 파란색)가 단위 속도로 돌 때의 tip 속도입니다.*

damped least squares는 역행렬 안에 `lam^2 I`(`I`는 단위행렬)를 더해서 0에 닿지 않게 합니다.

![Damped least squares](../assets/diagram-damping.png)

*속도는 더 이상 `|v| / (2 lam)`을 넘지 못합니다.*

![joint 속도와 tip 오차](../assets/fig-speed-blowup.png)

*실선은 lam = 0.05이고 점선은 0.15입니다. 왼쪽은 일반 역행렬이 `1 / q2`처럼 커지고 damped 해는 점선 상한 아래에 머무는 모습입니다. 오른쪽은 damped 해가 명령에 뒤처지는 모습입니다.*

## 만들기

```python
def solve(J, v, lam):
    if lam == 0.0: return np.linalg.solve(J, v)            # plain inverse
    return J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(len(v)), v)
```

`J`의 특이값 `s`는 `s / (s^2 + lam^2)`로 바뀌고 이 값은 `1 / (2 lam)`을 넘지 않습니다. 테스트가 확인하는 상한이 바로 이것입니다. `lam`이 작으면 명령을 가깝게 따르지만 빠르게 움직이고 `lam`이 크면 느리게 움직이지만 뒤처집니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/04-singularities -q
python3 phases/02-manipulator-kinematics/04-singularities/code/main.py
```

## 실제 도구로 보기

라이브러리는 작은 특이값에 cutoff를 둔 pseudo-inverse를 계산합니다. `q2 = 0.01` 근처에서 그 출력과 `solve`를 비교해 보세요.

## 결과물

`outputs/skill-singularity-guard.md`는 속도 controller 앞에 manipulability 감시와 damped solver를 두는 점검표입니다.

## 연습 문제

1. `manipulability(J)`가 문턱값 아래로 내려갈 때만 `lam`이 커지게 만드세요.
2. `q2 = 0.01`에서 joint 속도를 2 rad/s 아래로 유지하는 가장 작은 `lam`을 찾으세요.
3. 접힌 자세를 지나는 경로도 같은 문제를 겪는다는 것을 보이세요.
