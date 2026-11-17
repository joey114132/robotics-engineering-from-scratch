# 축-각과 Quaternion

> 로봇 손목이 왜 한 바퀴를 돌아가 버리는지, 그리고 그것을 막는 한 줄짜리 검사를 알게 됩니다.

**유형:** 만들기   **선수 지식:** 01/01 회전과 SE(3)   **시간:** 약 15분

## 쉽게 말하면

로봇 손목이 왼쪽으로 아주 조금 돌라는 명령을 받아요. 오른쪽으로 거의 한 바퀴를 돌아도 같은 방향에 닿아서 도착 방향만으로는 경로가 정해지지 않아요.

quaternion은 자세를 나타내는데 q와 그 반대인 -q가 같은 자세예요. 두 자세 사이를 매끄럽게 돌리는 slerp는 필요할 때 부호를 뒤집어 짧게 돌게 해요.

## 핵심 용어

- **Quaternion**: 자세를 나타내는 숫자 네 개입니다. 단위 quaternion은 길이가 1입니다.
- **Axis-angle**: 어떤 선을 축으로 얼마나 돌지를 각도로 적은 회전입니다.
- **Slerp**: 두 자세 사이를 같은 속도로 매끄럽게 돌리는 방법입니다.
- **Interpolator**: 시작 값과 목표 값 사이를 매끄럽게 움직이는 코드입니다.
- **Dot product**: 두 목록의 대응하는 성분끼리 곱해 더한 값으로 두 quaternion이 얼마나 닮았는지 알려 줍니다.
- **Radian (rad)**: 각도의 단위로 한 바퀴가 약 6.28입니다.

## 문제

로봇 손목에 아주 작은 오차를 고치라고 했는데 거의 한 바퀴를 반대 방향으로 돌았습니다. 목표가 부호가 뒤집힌 채 도착했고 자세 사이를 매끄럽게 이어 주는 코드가 그것을 그대로 믿었습니다.

## 개념

로봇은 자세 사이를 매끄럽게 돌리는 일을 늘 하고 부호 하나가 어긋나면 손목이 먼 쪽으로 돕니다.

![손목 두 개, 한 자세](../assets/clip-example.mp4)

*두 손목은 같은 자세로 끝납니다. 파랑은 조금 돌았고 초록은 조금에 한 바퀴를 더 돌았습니다.*

quaternion은 자세를 나타내는 숫자 네 개이고 모든 자세에는 서로 부호가 반대인 quaternion이 두 개 있습니다. 둘은 구의 반대편에 놓입니다.

![q와 -q](../assets/diagram-double-cover.png)

*구 위의 반대편 점 두 개는 같은 회전을 뜻합니다.*

해법은 목표가 먼 쪽에 있는지 확인해서 그렇다면 이어 주기 전에 부호를 뒤집는 것입니다.

![slerp 부호 확인](../assets/diagram-slerp-sign-fix.png)

*검사가 먼 쪽이라고 하면 부호를 뒤집고 짧은 길을 탑니다.*

![누적 각도](../assets/fig-slerp-long-way.png)

*보정이 없으면 손목이 거의 한 바퀴를 돌고 보정이 있으면 조금만 돕니다.*

<details><summary>The math (optional)</summary>

축 `k` 둘레로 각도 `t`만큼 도는 회전은 quaternion `(cos(t/2), sin(t/2) k)`입니다.
z축으로 0.1을 돌리면 `q = (0.9988, 0, 0, 0.0500)`이고 한 바퀴를 더하면(`t = 0.1 + 2pi`) `-q = (-0.9988, 0, 0, -0.0500)`이 됩니다.
`q0 = (1, 0, 0, 0)`과 `-q`의 dot product는 -0.9988이고 음수는 먼 쪽이라는 뜻이므로 뒤집습니다. 보정이 없으면 손목이 354.3도를 돌고 보정이 있으면 5.7도(0.1 rad)를 돕니다. 영상의 바늘은 반각 0.05와 pi + 0.05를 보여 줍니다.

</details>

## 만들기

`rodrigues`는 축과 각도를 회전 행렬로 바꿉니다. `slerp`는 두 자세 사이를 매끄럽게 이어 주고 `fix` 옵션은 dot product가 음수일 때 부호를 뒤집습니다.

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

SciPy의 `Rotation.from_quat`과 `Slerp`가 같은 일을 합니다. SciPy는 숫자 하나를 맨 뒤에 쓰고 이 레슨은 맨 앞에 쓰므로 라이브러리 경계를 넘을 때 순서를 확인하세요.

출처: Craig, *Introduction to Robotics*, 3판, 2장(Euler parameters, 절 번호는 확인하지 못했습니다).

## 결과물

`outputs/skill-quaternion-sign-check.md`는 자세를 보간하거나 비교하는 코드를 리뷰합니다.

## 연습 문제

1. `slerp`를 `fix=False`로 돌려서 먼 길로 도는 것을 보세요.
2. quaternion의 부호를 뒤집어도 같은 회전 행렬이 나오는지 확인하세요.
3. 부호 검사가 처음으로 뒤집히는 목표 각도를 찾으세요.
