# 회전과 SE(3)

> pose는 회전과 위치이고 곱하는 순서가 결과를 정합니다.

**유형:** 만들기   **선수 지식:** 없음   **시간:** 약 15분

## 쉽게 말하면

드론의 코가 문을 향하게 들어 보세요. 코를 축으로 직각만큼 굴린 다음 수직선을 축으로 직각만큼 돌리면 코가 왼쪽을 향해요. 먼저 돌리고 문 쪽 선을 축으로 굴리면 코가 천장으로 올라가요.

첫 번째 회전이 드론을 움직여 놓아서 두 번째 회전은 다르게 놓인 드론에 걸려요. 위치도 마찬가지예요. 이동을 먼저 하고 돌리면 그 회전이 드론을 원점 둘레로 데려가요. pose는 방향과 위치를 합친 것이고 pose를 순서대로 곱하면 둘을 함께 따라갈 수 있어요.

## 문제

카메라는 컵이 자기 frame(카메라에서 잰 x, y, z 방향)의 (0.2, 0, 0.5)에 있다고 봅니다. 팔에는 같은 컵이 base frame(팔의 base에서 잰 좌표)으로 필요합니다.

카메라의 transform과 컵의 transform을 잘못된 순서로 곱해도 결과는 그럴듯한 pose입니다. 다만 틀렸을 뿐이라서 팔은 존재하지 않는 점으로 손을 뻗는데 코드는 아무 경고도 내지 않습니다.

## 개념

회전 행렬 `R`은 물체를 늘이거나 뒤집지 않고 돌립니다. 세 열이 서로 수직이고 길이가 1이며(orthonormal) determinant(거울상인지 확인하는 값)가 +1이기 때문입니다. 거울상이면 -1이 됩니다.

rigid transform `T`는 `R`과 위치 `p`를 4x4 행렬 하나에 쌓은 것이고 SE(3)의 pose입니다. `T`를 점에 적용하면 `R`로 돌린 다음 `p`만큼 이동합니다. 곱 `A @ B`에서는 오른쪽 행렬이 먼저 작용하므로 순서가 중요합니다.

![transform과 inverse](../assets/diagram-transform-chain.png)

*번호를 따라가 보세요. `T_base_cam`은 카메라 좌표를 base 좌표로 옮기고 inverse는 되돌립니다.*

드론의 pose가 z축으로 직각 회전하고 `p = (1, 2, 0)`만큼 이동하는 것이라고 해 보겠습니다. 먼저 돌리고 이동하면 드론의 중심은 `p`에 놓이고 코에 찍은 점 (1, 0, 0)은 (1, 3, 0)에 놓입니다.

이동하고 돌리면 회전이 중심을 원점 둘레로 휘돌려 (-2, 1, 0)으로, 코의 점을 (-2, 2, 0)으로 보냅니다.

![반대 순서의 드론 두 대](../assets/clip-example.mp4)

*초록 드론은 돌고 나서 회색 목표로 이동합니다. 파란 드론은 먼저 이동해서 회전이 원점 둘레로 휘돌립니다.*

![회전 순서 두 가지](../assets/diagram-rotation-order.png)

*두 줄을 비교해 보세요. x축으로 굴린 뒤 z축으로 돌리거나 그 반대로 하면 코 (1, 0, 0)이 (0, 1, 0) 또는 (0, 0, 1)로 갑니다.*

inverse에는 closed form(식 하나로 바로 쓰는 공식) `[R^T, -R^T p]`가 있습니다. `R^T`(`R`의 행과 열을 맞바꾼 것)가 회전을 되돌리므로 `T^-1`은 먼저 이동을 되돌리고 그다음 회전을 되돌립니다.

일반 행렬 inverse는 drift를 숨깁니다. drift는 반올림된 곱셈이 쌓여 생기는 느린 오차인데 일반 inverse는 조금 틀어진 `R`을 조용히 뒤집기 때문입니다. closed form은 `R^T`가 `R`을 되돌린다고 믿으므로 drift가 있으면 `T^-1 T`가 항등 행렬에서 벗어납니다.

![float32 drift와 보정 효과](../assets/fig-rotation-drift.png)

*두 곡선을 비교해 보세요. float32(반올림된 숫자)로 작은 회전을 20,000번 곱하면 drift가 계속 커집니다. 100번마다 `R`을 되돌려 놓으면(`reorthonormalize`) 반올림 수준에 머뭅니다.*

## 만들기

```python
def is_rotation(R, tol=1e-9):
    return np.allclose(R.T @ R, np.eye(3), atol=tol) and np.isclose(np.linalg.det(R), 1.0, atol=tol)

def invert_T(T):
    R, p = T[:3, :3], T[:3, 3]
    return make_T(R.T, -R.T @ p)

def reorthonormalize(R):
    U, _, Vt = np.linalg.svd(R)
    return U @ np.diag([1, 1, np.linalg.det(U @ Vt)]) @ Vt
```

도우미 `rot_x`, `rot_y`, `rot_z`, `make_T`는 `code/main.py`에 있습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/01-rotations-and-se3 -q
```

## 실제 도구로 보기

`scipy.spatial.transform.Rotation`이 전부 해 줍니다. 마지막 테스트가 이것을 `rot_z(0.8)`과 비교합니다.

출처: Craig, *Introduction to Robotics*, 3판, 2장(공간 기술과 변환).

## 결과물

`outputs/skill-transform-sanity.md`는 이런 pose 버그가 하드웨어에 닿기 전에 잡는 체크리스트입니다.

## 연습 문제

1. `rot_x(a)`와 `rot_z(b)`를 두 순서로 합성하고 팁 위치의 차이를 출력하세요.
2. float64로 drift 곡선을 다시 그리세요. 몇 번째에서 `is_rotation`이 실패합니까?
3. transform 리스트를 곱하고 결과를 검사하는 `compose(Ts)`를 쓰세요.
