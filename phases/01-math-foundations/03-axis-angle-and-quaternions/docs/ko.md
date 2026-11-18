# 축-각과 Quaternion

> 로봇 손목이 왜 먼 길로 한 바퀴를 돌아 버리는지, 그리고 그것을 막는 한 줄짜리 검사를 알게 됩니다.

**유형:** 만들기   **선수 지식:** 01/01 회전과 SE(3)   **시간:** 약 15분

## 쉽게 말하면

로봇 손목이 왼쪽으로 아주 조금 돌라는 명령을 받아요. 오른쪽으로 거의 한 바퀴를 돌아도 거의 같은 쪽을 보게 돼요.

quaternion은 자세를 나타내는 숫자 네 개예요. 네 개의 부호를 모두 뒤집어도 같은 자세예요. 그래서 코드는 회전을 짧게 하려고 목표 자세의 부호를 뒤집을 수 있어요.

## 핵심 용어

- **Orientation**: 어떤 것이 어느 쪽을 보는지입니다.
- **Quaternion**: 자세를 나타내는 숫자 네 개입니다.
- **Slerp**: 두 자세 사이를 같은 속도로 매끄럽게 돌리는 방법입니다.
- **Dot product**: 두 quaternion의 대응하는 숫자끼리 곱해 더한 값입니다. 양수면 서로 가깝고 음수면 멉니다.
- **Radian (rad)**: 각도의 단위로 한 바퀴가 약 6.28입니다.

## 문제

로봇 손목에 아주 작은 오차를 고치라고 했는데 먼 길로 거의 한 바퀴를 돌았습니다. 목표가 부호가 뒤집힌 채 도착했고 코드가 그것을 그대로 믿었습니다.

## 개념

부호 하나가 어긋나면 손목이 먼 쪽으로 돕니다.

![손목 두 개, 한 자세](../assets/clip-example.mp4)

*두 손목은 같은 자세로 끝납니다. 파랑은 조금 돌았고 초록은 거기에 한 바퀴를 더 돌았습니다.*

모든 자세에는 quaternion이 두 개 있습니다. 하나를 q라고 하면 네 부호를 모두 뒤집은 다른 하나는 -q입니다.

![q와 -q](../assets/diagram-double-cover.png)

*q와 -q는 서로 다른 숫자이지만 같은 회전을 줍니다.*

해법은 두 quaternion의 dot product를 구하는 것입니다. 두 자세가 가까우면 양수이고 멀면 음수입니다. 음수이면 목표가 먼 길 쪽에 있다는 뜻이므로 매끄러운 회전(slerp) 전에 부호를 뒤집습니다.

![slerp 부호 확인](../assets/diagram-slerp-sign-fix.png)

*검사가 먼 쪽이라고 하면 부호를 뒤집고 짧은 길을 탑니다.*

![누적 각도](../assets/fig-slerp-long-way.png)

*보정이 없으면 손목이 거의 한 바퀴를 돌고 보정이 있으면 조금만 돕니다.*

<details><summary>The math (optional)</summary>

축 `k` 둘레로 각도 `t`만큼 도는 회전은 quaternion `(cos(t/2), sin(t/2) k)`입니다.
z축으로 0.1을 돌리면 `q = (0.9988, 0, 0, 0.0500)`이고 한 바퀴를 더하면(`t = 0.1 + 2pi`) `-q = (-0.9988, 0, 0, -0.0500)`이 됩니다.
`q0 = (1, 0, 0, 0)`과 `-q`의 dot product는 -0.9988이고 음수는 먼 쪽이라는 뜻이므로 뒤집습니다. 보정이 없으면 손목이 354.3도를 돌고 보정이 있으면 5.7도(0.1 rad)를 돕니다. 영상의 바늘은 반각 0.05와 pi + 0.05를 보여 줍니다.
SciPy는 quaternion의 숫자 네 개를 이 레슨과 다른 순서로 적으므로 라이브러리를 바꿀 때 순서를 확인하세요.

</details>

## 만들기

`rodrigues`는 축과 각도를 회전 행렬로 바꿉니다. `slerp`는 두 자세 사이를 매끄럽게 돌리고 `fix` 옵션은 dot product가 음수일 때 부호를 뒤집습니다.

```python
def rodrigues(axis, angle):
    k = _unit(axis)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * K @ K

def slerp(q0, q1, t, fix=True):
    d = float(q0 @ q1)
    if fix and d < 0:
        q1, d = -q1, -d
    om = np.arccos(min(d, 1.0))
    return (np.sin((1 - t) * om) * q0 + np.sin(t * om) * q1) / np.sin(om)
```

전체 파일에는 `quat_mul`, `quat_to_R`, `R_to_quat`이 더 들어 있습니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/03-axis-angle-and-quaternions -q
```

## 실제 도구로 보기

SciPy는 Python 도구이고 `Rotation.from_quat`과 `Slerp`가 같은 일을 합니다.

출처: Craig, *Introduction to Robotics*, 3판, 2장(Euler parameters, 절 번호는 확인하지 못했습니다).

## 결과물

`outputs/skill-quaternion-sign-check.md`는 자세를 보간하는 코드를 리뷰합니다.

## 연습 문제

1. `slerp`를 `fix=False`로 돌려서 먼 길로 도는 것을 보세요.
2. quaternion의 부호를 뒤집어도 같은 회전 행렬이 나오는지 확인하세요.
3. 목표를 조금씩 움직이면서 dot product가 처음으로 음수가 되는 곳을 찾으세요.
