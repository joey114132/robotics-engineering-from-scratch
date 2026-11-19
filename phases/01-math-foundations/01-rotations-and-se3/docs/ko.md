# 회전과 SE(3)

> 물체가 어디에 있고 어느 쪽을 보는지 나타내는 법과, 회전 두 개의 순서가 왜 중요한지 알게 됩니다.

**유형:** 만들기   **선수 지식:** 없음   **시간:** 약 15분

## 쉽게 말하면

드론의 코가 문을 향하게 들어 보세요. 문까지 이은 선을 축으로 직각만큼 굴린 다음 수직선을 축으로 직각만큼 돌리면 코가 왼쪽을 향해요. 먼저 돌리고 같은 선을 축으로 굴리면 코가 천장으로 올라가요.

pose는 어느 쪽을 보는지와 어디에 있는지를 합친 것이에요. pose를 순서대로 합치면 방향과 위치를 함께 따라갈 수 있어요. 이때 순서가 중요해요.

## 핵심 용어

- **Rotation matrix**: 점을 늘이지 않고 돌리는 3x3 숫자 표입니다.
- **Pose**: 물체가 어느 쪽을 보는지와 어디에 있는지를 합친 것입니다.
- **Transform (`T`)**: 회전과 이동을 한 표에 담은 4x4 행렬입니다.
- **Frame**: 카메라나 팔의 base 같은 대상에 붙은 x, y, z축입니다.
- **Inverse**: 다른 transform을 되돌리는 transform입니다.
- **Drift**: 반올림된 숫자를 여러 번 곱하면서 쌓이는 느린 오차입니다.

## 문제

마스트에 달린 카메라가 컵을 보고 팔은 자기 base에서 잰 컵의 위치가 필요합니다. 카메라의 pose와 컵의 pose를 잘못된 순서로 합치면 팔은 거기 없는 점으로 손을 뻗습니다.

## 개념

로봇은 각 부품이 어디에 있고 어느 쪽을 보는지 알아야 합니다.

![transform과 inverse](../assets/diagram-transform-chain.png)

*pose 하나로 카메라의 시점에서 base의 시점으로 가는 방법을 알 수 있습니다.*

돌리고 이동하는 것과 이동하고 돌리는 것은 다른 곳에 닿습니다.

[![반대 순서의 드론 두 대](../assets/clip-example.jpg)](../assets/clip-example.mp4)

*초록은 먼저 돌고 나서 이동합니다. 파랑은 먼저 이동하므로 회전할 때 원점을 중심으로 크게 휘돌아 갑니다.*

![회전 순서 두 가지](../assets/diagram-rotation-order.png)

*같은 회전 두 개도 순서가 다르면 코가 다른 방향을 가리킵니다.*

반올림 오차 때문에 회전 행렬은 서서히 진짜 회전에서 벗어납니다. 그래서 오래 도는 프로그램은 가끔 이를 바로잡습니다.

![drift와 보정 효과](../assets/fig-rotation-drift.png)

*바로잡지 않으면 오차가 계속 커지고 바로잡으면 오차가 아주 작게 유지됩니다.*

<details><summary>The math (optional)</summary>

회전 행렬 `R`은 열이 서로 수직이고 길이가 1이며 determinant가 +1입니다. pose `T`는 `R`과 위치 `p`를 4x4 행렬 하나에 쌓은 것으로 점을 `R`로 돌린 다음 `p`만큼 이동합니다. `A @ B`에서는 오른쪽 행렬이 먼저 작용합니다.
inverse는 `[R^T, -R^T p]`입니다. 이런 4x4 pose 전체를 제목에 있는 SE(3)라고 부릅니다. z축으로 직각만큼 돌리고 `p = (1, 2, 0)`이라고 해 봅니다. 돌린 다음 이동하면 (1, 0, 0)이 (1, 3, 0)이 되고 이동한 다음 돌리면 (-2, 2, 0)이 됩니다.
float32로 작은 회전을 20,000번 곱하면 drift가 생깁니다. 100번마다 `reorthonormalize`를 하면 오차가 반올림 수준에 머뭅니다.

</details>

## 만들기

작은 도우미 세 개가 행렬이 진짜 회전인지 검사하고 pose를 되돌리고 어긋난 회전을 바로잡습니다.

```python
def is_rotation(R, tol=1e-9):
    return np.allclose(R.T @ R, np.eye(3), atol=tol, rtol=0.0) and np.isclose(np.linalg.det(R), 1.0, atol=tol, rtol=0.0)

def invert_T(T):
    R, p = T[:3, :3], T[:3, 3]
    return make_T(R.T, -R.T @ p)

def reorthonormalize(R):
    U, _, Vt = np.linalg.svd(R)
    return U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
```

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/01-rotations-and-se3 -q
```

## 실제 도구로 보기

SciPy는 Python 도구이고 `Rotation`이 이 모든 일을 해 줍니다. 테스트 하나가 이 레슨에서 z축으로 0.8 radians 돌린 회전과 결과를 비교합니다.

출처: Craig, *Introduction to Robotics*, 3판, 2장.

## 결과물

`outputs/skill-transform-sanity.md`는 이런 pose 버그가 하드웨어에 닿기 전에 잡는 체크리스트입니다.

## 연습 문제

1. 점을 z축 둘레로 90도 돌리고 이동한 다음 순서를 바꿔 보고 답이 어떻게 다른지 보세요.
2. 아주 작은 회전을 수천 번 곱한 다음 만들기의 회전 검사를 돌려 보세요.
3. pose 리스트를 곱하는 `compose`를 쓰세요.
