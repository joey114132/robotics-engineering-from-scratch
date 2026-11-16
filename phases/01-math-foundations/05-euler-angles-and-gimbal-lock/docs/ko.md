# Euler 각도와 Gimbal Lock

> 도구가 바로 아래로 기울면 roll, pitch, yaw 숫자가 왜 갑자기 튀는지 알게 됩니다.

**유형:** 만들기   **선수 지식:** 01/01 회전과 SE(3), 01/03 축-각과 Quaternion   **시간:** 약 15분

## 쉽게 말하면

카메라가 겹쳐진 고리 세 개 안에 있어요. 고리들은 카메라를 수직선 둘레로 돌리고 기울이고 보는 선을 축으로 굴려요. 바로 아래로 기울이면 고리 두 개가 같은 선을 축으로 화면을 비틀어요.

그 자세 근처에서는 같은 화면에 고리 설정이 두 가지예요. 고리 각도를 읽는 코드는 그중 하나만 알려 주기 때문에 카메라는 매끄럽게 움직이는데 yaw와 roll 값은 갑자기 뛰어요.

## 핵심 용어

- **Euler angles**: roll, pitch, yaw라고 부르는, 정해진 순서로 적용하는 회전 세 개입니다.
- **Roll, pitch, yaw**: 앞쪽 축, 옆쪽 축, 수직 축을 도는 회전입니다.
- **Gimbal lock**: 고리 두 개가 나란해져서 돌릴 수 있는 방향 하나를 잃은 자세입니다.
- **Euler rates**: 각 고리가 돌고 있는 속도입니다.
- **Determinant (`det`)**: 행렬에서 계산하는 숫자 하나입니다. 0이면 그 행렬이 공간을 납작하게 만듭니다.
- **Low-pass filter**: 빠른 변화를 흐리게 만드는 평활기입니다.

## 문제

로봇에 달린 카메라가 roll, pitch, yaw를 보고합니다. 바로 아래로 기울어지면 roll과 yaw가 갑자기 180도 튀거나 제어기가 엄청나게 빠른 관절 속도를 요구합니다.

센서는 멀쩡하고 문제는 각도 형식에 있습니다.

## 개념

많은 로봇 센서가 자세를 각도 세 개로 알려 주는데 한 자세 근처에서는 그 세 숫자가 의미를 잃습니다.

Euler 각도는 정해진 순서의 회전 세 번으로 자세를 나타냅니다. 수직 z축을 도는 yaw, 옆 y축을 도는 pitch, 앞 x축을 도는 roll입니다. `R = Rz(yaw) Ry(pitch) Rx(roll)`에서는 roll이 먼저 작용합니다.

![고리가 방향 하나를 잃습니다](../assets/diagram-gimbal-rings.png)

*pitch가 90도이면(gimbal lock) roll 고리가 yaw 고리와 나란해집니다.*

이때 두 고리는 같은 수직선을 축으로 돌고 roll `+a`는 yaw `-a`와 같습니다. `yaw - roll`만 의미가 있고 돌릴 수 있는 방향 하나를 잃습니다.

![고리 장치 두 개, 한 자세](../assets/clip-example.mp4)

*왼쪽은 roll 고리를 +1.2 rad, 오른쪽은 yaw 고리를 -1.2 rad 돌립니다. 주황색 fin이 같은 방향을 가리키며 끝납니다.*

`R`에서 각도를 다시 읽으면 pitch는 -90도에서 90도 사이로만 나옵니다. 그래서 90도를 넘으면 읽는 쪽이 roll과 yaw가 180도 떨어진 두 번째 표기(`other_spelling()`)로 바꿉니다.

![매끄러운 회전, 점프](../assets/diagram-angle-jump.png)

*도구는 매끄럽게 움직이는데 roll과 yaw는 180도 뒤집힙니다.*

Euler rate에는 3x3 행렬 `E`가 필요하고 `det E = cos(pitch)`입니다. 90도에서는 이 값이 0이라서 어떤 회전은 Euler rate로 만들 수 없습니다.

![점프와 rate 폭주](../assets/fig-gimbal-lock.png)

*왼쪽은 pitch를 60도에서 120도까지 돌린 결과입니다. 오른쪽은 yaw 0에서 world-x 축으로 1 rad/s 회전할 때 Euler rate가 1 / cos(pitch)처럼 커지는 모습입니다.*

## 만들기

```python
def euler_to_R(roll, pitch, yaw):
    return _rot(2, yaw) @ _rot(1, pitch) @ _rot(0, roll)
```

`R_to_euler()`는 pitch를 `-R[2, 0]`에서 읽습니다. lock에서 1e-9 이내이면 `locked=True`를 돌려주고 roll을 0으로 둡니다. +90도에서는 `yaw - roll`만 정해지기 때문입니다.

`euler_rates()`는 gimbal lock에서 예외를 냅니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/05-euler-angles-and-gimbal-lock -q
python3 phases/01-math-foundations/05-euler-angles-and-gimbal-lock/code/main.py
```

## 실제 도구로 보기

`R_to_euler()`를 SciPy의 `Rotation.as_euler("ZYX")`와 비교하세요. SciPy는 gimbal lock에서 경고를 내므로 각도가 아니라 회전을 비교합니다.

## 결과물

`outputs/skill-euler-angle-audit.md`는 제어, 로그, 필터에 Euler 각도를 쓰는 곳이 있는지 점검합니다.

## 연습 문제

1. pitch 90도에서 같은 `R`을 주는 다른 `(roll, yaw)` 쌍을 찾으세요.
2. yaw 0, pitch 89.9도에서 world-x 축으로 1 rad/s 회전할 때 가장 큰 Euler rate를 구하세요.
3. 점프 구간에서 각도에 건 low-pass filter와 `R`에 건 slerp를 비교하세요.
