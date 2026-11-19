# 수치 Inverse Kinematics

> joint 한계와 재시작을 다루며 작은 수정의 반복으로 joint 각도를 찾는 법을 알게 됩니다.

**유형:** 만들기   **선수 지식:** 02/03 Jacobian과 속도, 02/04 Singularity   **시간:** 약 15분

## 쉽게 말하면

link가 세 개인 작은 로봇 팔이 작은 수정을 반복해서 공에 닿으려 해요. 관절을 조금 꺾어 보고 손이 어디로 갔는지 본 다음 고쳐요. 크게 꺾으면 공을 지나칠 수 있고 끝까지 꺾인 관절은 더 꺾이지 않아요.

numerical inverse kinematics는 이런 작은 수정을 되풀이하는데 수정마다 Jacobian으로 손이 어떻게 움직일지 예측해요. 시작 자세에 따라 찾는 답이 달라져서 여러 자세에서 다시 시작해요.

## 핵심 용어

- **Numerical IK**: 공식 대신 작은 수정을 반복해서 관절 각도를 찾는 방법입니다.
- **Seed**: 한 번의 실행이 시작하는 자세입니다.
- **Joint limit**: 관절이 돌 수 있는 범위이고 거기서 관절이 멈춥니다.
- **Clamp**: 값을 허용 범위 안으로 잘라 내는 것입니다.
- **Converged**: 오차가 허용값 아래로 내려온 상태입니다. 여기서는 100만 분의 1 m입니다.
- **Jacobian**: 관절을 조금 움직였을 때 tip이 어떻게 움직일지 예측하는 숫자 표입니다.

## 문제

로봇 팔이 바뀔 때마다 새 공식을 유도하지 않고 손을 목표에 놓고 싶습니다. 각도는 관절 한계를 지켜야 합니다. 한 시작점에서는 막힐 수 있으므로 여러 시작점을 시도합니다.

## 개념

직접 구하는 공식이 불편할 때는 시도하고 고치면서 각도를 찾을 수 있습니다. 손이 어디 있는지 보고 빗나간 만큼을 잽니다. 그 빗나감을 줄이도록 관절을 조금 움직이고 빗나감이 아주 작아질 때까지 되풀이합니다.

![반복 한 걸음](../assets/diagram-ik-loop.png)

*빗나감을 재고 움직이고 확인하고 되풀이합니다.*

조금씩 움직이면 각 수정이 정확하게 유지됩니다. 한계에 닿은 관절은 그 자리에 붙들어 둡니다. 출발점에 따라 찾는 답이 달라지므로 로봇은 무작위 출발점 여러 개를 시도합니다.

![무작위 시작 자세가 여러 개의 해로 수렴하는 모습](../assets/diagram-ik-restarts.png)

*출발점마다 가까운 답으로 미끄러져 들어갑니다.*

![흐릿한 팔과 수렴](../assets/fig-numerical-ik.png)

*흐릿한 팔은 걸음을 보여 줍니다. 닿는 목표는 빗나감이 줄고 닿지 않는 목표는 평평하게 남습니다.*

[![같은 공에 닿는 두 시작 자세](../assets/clip-example.jpg)](../assets/clip-example.mp4)

*출발점 둘, 팔 모양 둘, 공은 하나입니다.*

<details><summary>The math (optional)</summary>

각 수정은 02/04의 damped solve `dq = J^T (J J^T + lam^2 I)^-1 e`이고 `e`는 빗나감입니다. 가장 큰 관절 걸음에는 상한을 둡니다. 수렴은 빗나감이 1e-6 m 아래로 내려온 것입니다. 닿는 목표는 약 16걸음 안에 수렴합니다.
link 0.4, 0.3, 0.2 m와 목표 (0.5, 0.3) m에서 무작위 출발점 20개 중 17개가 수렴합니다. 출발점 0은 6걸음(elbow up), 출발점 2는 7걸음(elbow down)입니다.

</details>

## 만들기

반복 한 걸음은 세 줄입니다. 표를 만들고 작은 움직임을 구한 다음 관절 한계로 clamp합니다.

```python
J = jacobian(q, L)
dq = J.T @ np.linalg.solve(J @ J.T + lam**2 * np.eye(2), e)
q = np.clip(q + dq * min(1.0, max_step / np.abs(dq).max()), lo, hi)
```

`solve_ik()`는 각도와 수렴 여부를 돌려줍니다. 실패하면 방문한 자세 중 오차가 가장 작은 것을 주며 가장 가까운 자세를 보장하지는 않습니다. `ik_restarts()`는 무작위 출발점을 시도합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/05-numerical-inverse-kinematics -q
python3 phases/02-manipulator-kinematics/05-numerical-inverse-kinematics/code/main.py
```

## 실제 도구로 보기

빗나감에 `scipy.optimize.least_squares`를 적용하고 관절 한계를 bounds로 주어 비교하세요. 직접 구하는 공식은 Craig 4장에 나옵니다.

## 결과물

`outputs/skill-ik-solver-check.md`는 IK solver의 한계 처리, 재시작, 실패 flag를 점검합니다.

## 연습 문제

1. 지금 pose에 가장 가까운 답을 고르세요.
2. 네 번째 link를 더하고 몇 번의 출발이 성공하는지 세어 보세요.
3. 완전히 쭉 펴진 팔에서 시작해서 solver가 무엇을 하는지 말해 보세요.
