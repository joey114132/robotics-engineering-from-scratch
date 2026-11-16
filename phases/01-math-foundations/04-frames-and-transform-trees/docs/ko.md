# Frame과 Transform 트리

> 위치가 어느 부품의 시점에서 잰 것인지 헷갈리지 않게 해 주는 이름 짓기 습관을 알게 됩니다.

**유형:** 만들기   **선수 지식:** 01/01 회전과 SE(3)   **시간:** 약 15분

## 쉽게 말하면

마스트에 달린 카메라가 카메라에서 잰 컵의 위치를 알려 줘요. 팔에는 자기 base에서 잰 위치가 필요한데 카메라는 반대쪽을 보고 있어서 그 숫자를 그대로 쓰면 팔이 엉뚱한 곳을 향해요.

transform tree는 각 frame(부품에 붙은 x, y, z 방향)이 부모 안에 어떻게 놓이는지를 저장해요. 컵의 위치를 바꾸려면 사슬을 따라 transform을 곱해요.

## 핵심 용어

- **Frame**: 카메라나 base 같은 부품에 붙은 x, y, z 방향의 묶음입니다.
- **Transform tree**: 모든 frame이 부모 frame 하나에 매달린 지도입니다.
- **`T_to_from`**: `from` frame의 좌표를 `to` frame의 좌표로 바꾸는 transform입니다.
- **Common ancestor**: 트리에서 두 frame 위쪽의 가장 가까운 frame으로 두 경로가 만나는 곳입니다.
- **Cycle**: frame이 자기 자신의 조상이 되는 고리입니다.
- **tf2**: transform 트리를 저장하는 ROS 2 라이브러리입니다.

## 문제

카메라는 컵을 보고 팔은 자기 base에서 잰 컵의 위치가 필요합니다. 누군가 `T_cam_cup @ T_base_cam`을 쓰거나 엉뚱한 행렬에 inverse를 씌웁니다.

`cam`과 `base`라는 이름에 방향이 없기 때문입니다. 두 결과 모두 엉뚱한 곳을 가리키는 유효한 pose입니다.

## 개념

로봇의 부품은 저마다 자기 자리에서 세상을 보므로 모든 측정값을 올바른 시점으로 바꿔 주어야 합니다.

`T_to_from`은 `from`의 좌표를 `to`의 좌표로 바꿉니다. 곱에서는 안쪽 이름이 상쇄됩니다. `T_a_b @ T_b_c = T_a_c`입니다.

![frame마다 부모가 하나인 트리](../assets/diagram-tf-tree.png)

*화살표마다 `T_parent_child`가 저장되어 있습니다. 카메라와 손은 둘 다 base에 달려 있습니다.*

손이 보는 컵의 위치를 구하려면 두 frame에서 공통 조상까지 올라간 다음 한쪽을 inverse로 내려갑니다.

![조회는 공통 조상까지 올라갑니다](../assets/diagram-tf-lookup.png)

*`T_tool_cup`을 구하려면 `base`까지 올라간 뒤 `inv(T_base_tool) @ T_base_cup`을 씁니다.*

카메라가 base frame의 (0.5, 0, 0.4)에 반대쪽을 향해 있고 컵이 카메라 frame의 (0.2, 0, 0.5)에 있다고 해 보세요.

카메라의 x축은 base 쪽을 가리키므로 base frame에서 컵은 (0.3, 0, 0.9)에 있습니다. (0.3, 0, 0.7)에 있는 손에게는 컵이 (0, 0, 0.2)로 보입니다.

![같은 컵을 카메라와 base와 손에서 잰 모습](../assets/clip-example.mp4)

*진한 파란색 화살표는 카메라에서, 초록색은 base에서, 주황색은 손에서 나옵니다.*

![잘못된 곱의 비용](../assets/fig-wrong-order-error.png)

*이 배치에서 곱의 순서를 바꾸면 최대 0.4 m, inverse를 잘못 쓰면 최대 1.3 m 어긋납니다.*

## 만들기

```python
def lookup(self, to, frm):
    up_to, up_from = self._up(to), self._up(frm)
    common = next((f for f in up_from if f in up_to), None)
    if common is None:
        raise ValueError(f"{to} and {frm} are in different trees")
    return invert_T(self._to_ancestor(to, common)) @ self._to_ancestor(frm, common)
```

`add()`는 두 번째 부모와 cycle을 거부합니다. `_to_ancestor()`는 올라가는 길에 저장된 transform을 곱합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/04-frames-and-transform-trees -q
```

## 실제 도구로 보기

ROS 2의 `tf2`도 같은 구조이고 `lookup_transform(target, source, time)`은 target을 먼저 받습니다. 같은 트리에서 그 결과를 `TFTree.lookup`과 비교해 보세요.

출처: 이 시그니처는 로컬 ROS 2 Jazzy 설치의 `tf2_ros/buffer.py`에서 확인했습니다.

## 결과물

`outputs/skill-frame-naming-review.md`는 코드 리뷰에서 transform 곱과 frame 이름을 점검합니다.

## 연습 문제

1. `cam` 아래에 `static_cam_cup` frame을 추가하고 사슬이 여전히 상쇄되는지 확인하세요.
2. `lookup`이 지나간 frame 목록을 돌려주게 하세요.
3. 각 edge에 `time`이 있으면 `lookup`에 어떤 보간이 필요한지 말해 보세요.
