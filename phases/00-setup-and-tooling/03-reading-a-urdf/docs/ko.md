# URDF 읽기

> URDF는 joint로 이어진 link의 tree이고 모든 joint origin은 부모 link의 frame에서 쓰여 있습니다.

**유형:** 만들기   **선수 지식:** 00/01 Python 환경과 numpy   **시간:** 약 15분

## 쉽게 말하면

작은 bench arm의 파일에는 팔꿈치가 어깨에서 일정한 거리만큼 앞에 있다고 적혀 있어요. 여기서 앞은 방이 아니라 link를 따라가는 방향이라서 어깨를 돌리면 앞이 옆을 가리켜요.

URDF는 로봇의 설명 파일이고 joint로 이어진 link(단단한 부품)를 나열해요. 각 joint의 offset은 바로 앞 link의 frame, 곧 그 link 자신의 x, y, z축을 기준으로 적혀 있어요.
offset마다 그 앞에서 일어난 회전을 모두 반영한 다음 더해야 해요. 적힌 offset을 그대로 더하면 앞이 늘 같은 방향이라고 보는 셈이에요.

## 문제

offset을 모두 더해서 손의 위치를 구했는데 viewer가 보여 주는 위치와 많이 다릅니다. offset 값은 맞았습니다.

각 값을 world frame, 곧 방에 고정된 x, y, z축으로 읽었지만 파일은 바로 앞 link의 축을 기준으로 씁니다.

## 개념

base에서 손까지 화살표를 따라가 보세요.

![URDF tree](../assets/diagram-urdf-tree.png)

*상자는 link이고 화살표는 joint입니다(graph의 node와 edge). link는 자식을 여럿 가질 수 있지만 부모 joint는 하나뿐입니다.*

joint마다 부모, 자식, `<origin>`(위치 `xyz`와 회전 `rpy`)이 있고 움직이는 joint에는 axis와 limit도 있습니다.

ROS wiki는 origin을 부모 link에서 자식 link로 가는 transform으로 정의합니다. `rpy`는 고정축 기준으로 x축 roll, y축 pitch, z축 yaw 순서의 회전입니다.

같은 `xyz`를 두 가지로 읽은 결과를 비교해 보세요.

![Which frame](../assets/diagram-origin-frame.png)

*부모 frame에서 읽으면 elbow offset은 돌아간 link를 따라갑니다. world frame에서 읽으면 회전을 무시합니다.*

여기서는 모든 joint 각도가 0이고 회전은 파일 안에 있습니다. 어깨 `<origin>`이 frame을 z축 방향으로 0.1 m 올리고 z축 둘레로 90도 돌려 x를 y 위로 보냅니다.

elbow offset은 `0.3 0 0`, wrist offset은 `0.2 0 0`이고 각각 자기 link의 x축 방향입니다. world 방향으로 더하면 `(0.5, 0, 0.1)`이 나옵니다.

제대로 돌리면 둘 다 world y 방향이어서 손은 `(0, 0.5, 0.1)`에 있고 틀린 답과 0.71 m 떨어져 있습니다.

![Offsets read two ways](../assets/clip-example.mp4)

*URDF 크기의 두 배입니다. 어두운 축이 90도 돌고 초록 화살표가 따라갑니다. 연한 파란 화살표는 world x축에 머뭅니다. 빨간 선은 두 손 사이의 거리입니다.*

![Top view](../assets/fig-origin-frames.png)

*위에서 본 모습입니다. 어깨 origin이 팔을 90도 돌리므로 elbow offset은 y 방향을 향합니다. offset을 그냥 더하면 손이 맞는 답에서 0.71 m 벗어납니다.*

## 만들기

표준 라이브러리로 파싱한 다음 root에서 tip까지 걸어가며 joint마다 4x4 transform(회전과 이동을 함께 담은 표) 하나씩 곱합니다.

```python
root = ET.fromstring(xml)
for e in root.findall("joint"):
    o = e.find("origin")
    joints[e.get("name")] = dict(parent=e.find("parent").get("link"),
                                 child=e.find("child").get("link"),
                                 xyz=_vec(o, "xyz"), rpy=_vec(o, "rpy"))
# T = T @ T_origin @ R_axis(q), for each joint on the chain
```

`chain()`은 tip에서 root까지 부모 link를 따라갑니다. `link_positions()`는 origin을 먼저 적용하고 joint 회전을 그다음에 적용하며 limit 밖의 값은 거부합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/00-setup-and-tooling/03-reading-a-urdf -q
```

## 실제 도구로 보기

ROS 2에서는 `robot_state_publisher`가 URDF와 `joint_states` topic(joint 값을 담은 이름 있는 스트림)을 받아 pose를 ROS의 frame 저장소인 tf2로 publish합니다.

같은 joint 값에서 그 transform을 `link_positions()`의 결과와 비교해 보세요.

출처: https://wiki.ros.org/urdf/XML/joint, https://github.com/ros/robot_state_publisher

## 결과물

`outputs/skill-urdf-reading-check.md`는 URDF 위치가 이상할 때 확인할 항목을 정리한 것입니다.

## 연습 문제

1. prismatic joint를 추가하고 link를 axis 방향으로 움직이세요.
2. 자식이 둘 이상인 link를 모두 출력하세요.
3. root가 둘인 tree를 파서가 거부하게 만드세요.
