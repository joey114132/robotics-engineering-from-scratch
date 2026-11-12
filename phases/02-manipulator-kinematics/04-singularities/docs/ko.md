# Singularity와 damped least squares

> 팔이 펴지면 tip이 움직일 수 있는 방향이 하나 사라지고 일반 역행렬은 한없이 커지는 joint 속도로 대답합니다.

**유형:** 만들기   **선수 지식:** 02/03 Jacobian   **시간:** 약 15분

## 쉽게 말하면

어깨를 고정하고 구부린 팔을 펴면 손끝을 바깥으로 보낼 수 있어요. 거의 다 편 상태에서는 같은 바깥쪽 손끝 속도를 내려면 joint가 훨씬 빨리 돌아야 해요. 완전히 펴면 joint 회전으로 순간적인 바깥쪽 속도를 만들 수 없어요.

이 자세가 singularity예요. 근처에서 Jacobian을 그대로 역으로 풀면 joint 속도가 크게 치솟아요. damped least squares는 tip 속도에 오차를 허용해 이 증폭을 줄여요. damping을 키우면
joint 속도는 줄지만 목표 속도와 더 어긋나요.

## 문제

tip을 바깥쪽으로 곧게 0.1 m/s로 움직이라고 명령합니다. 팔이 완전히 뻗는 자세에 가까워지면 controller가 elbow에 초당 100 라디안을 요구하고 drive가 포화되어 tip이 경로를 벗어납니다.

고장 난 것은 없습니다. Jacobian이 방향 하나를 잃었는데 controller가 그래도 역행렬을 구하려 했을 뿐입니다.

## 개념

![일이 벌어지는 순서](../assets/diagram-chain.png)

*elbow 각이 줄면 `det J`가 줄어듭니다. tip 방향 하나가 사라지고 역행렬은 엄청난 속도를 요구합니다.*

이 팔은 `det J = L1 L2 sin q2`이므로 완전히 뻗거나 완전히 접히면 singular입니다(Craig 5장 5.8절). manipulability `sqrt(det(J J^T))`는 elbow가 직각일 때 가장 큽니다.

singularity에서 `J`의 rank는 1이고 어떤 joint 속도로도 tip을 반지름 방향으로 움직일 수 없습니다.

![Damped least squares](../assets/diagram-damping.png)

*Damped least squares는 역행렬 안에 `lam^2 I`를 더합니다. 속도는 더 이상 `|v| / (2 lam)`을 넘지 못합니다.*

![joint 속도와 tip 오차](../assets/fig-speed-blowup.png)

*왼쪽은 일반 역행렬이 `1 / q2`처럼 커지고 damped 해는 각자의 상한 아래에 머무는 모습입니다. 오른쪽은 damped 해가 singularity 근처에서 명령을 따라가지 못하는 모습입니다.*

## 만들기

```python
def solve(J, v, lam):
    if lam == 0.0: return np.linalg.solve(J, v)            # plain inverse
    return J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(len(v)), v)
```

`J`의 특이값 `s`는 `s / (s^2 + lam^2)`로 바뀌고 이 값은 `1 / (2 lam)`을 넘지 않습니다. 테스트가 확인하는 상한이 바로 이것입니다. `lam`은 절충입니다. 작으면 명령을 가깝게 따르지만 빠르게 움직이고 크면 느리게 움직이지만 뒤처집니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/04-singularities -q
python3 phases/02-manipulator-kinematics/04-singularities/code/main.py
```

## 실제 도구로 보기

라이브러리는 작은 특이값에 cutoff를 둔 pseudo-inverse를 계산합니다. `q2 = 0.01` 근처에서 그 출력과 `solve`를 비교하고 cutoff나 damping을 어떻게 고르는지 읽어 보세요.

## 결과물

`outputs/skill-singularity-guard.md`는 속도 controller 앞에 manipulability 감시와 damped solver를 두는 점검표입니다.

## 연습 문제

1. `manipulability(J)`가 문턱값 아래로 내려갈 때만 `lam`이 커지게 만드세요.
2. `q2 = 0.01`에서 joint 속도를 2 rad/s 아래로 유지하는 가장 작은 `lam`을 찾으세요.
3. 접힌 자세를 지나는 경로도 뻗은 자세를 지나는 경로와 같은 문제를 겪는다는 것을 보이세요.
