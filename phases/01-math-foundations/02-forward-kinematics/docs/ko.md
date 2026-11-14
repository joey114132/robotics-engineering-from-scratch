# 순기구학 (Forward Kinematics)

> 사슬을 따라 걷습니다. 관절에서 회전하고 link를 따라 한 걸음 나아가고 이를 반복합니다.

**유형:** 만들기   **선수 지식:** 01/01 회전과 SE(3)   **시간:** 약 15분

## 쉽게 말하면

작은 책상용 로봇 팔에는 어깨에 모터가 하나, 팔꿈치에 모터가 하나 있어요. 어깨를 돌리면 팔 전체가 함께 움직여요. 팔꿈치를 돌리면 그 바깥쪽의 아래팔과 손만 팔꿈치 둘레로 돌아요.

forward kinematics는 이 회전을 base에서 손까지 따라가요. 관절 사이의 막대가 link이고 link가 향하는 방향에는 앞쪽 관절 각도가 모두 더해져 있어요. 그 방향으로 link 길이만큼 나아가고 모든 걸음을 더하면 손끝이 어디에 닿는지 알 수 있어요.

## 문제

제어기는 관절각을 알지만 과제는 Cartesian 공간(x, y 위치)에 있습니다. gripper(손)를 (0.5, 0.3)에 놓아야 합니다. 순기구학(FK)은 관절각을 팁 pose로 옮깁니다.

역기구학(원하는 팁에 맞는 각도 찾기)과 Jacobian(관절 속도에 따라 팁 속도가 어떻게 변하는지)과 충돌 검사가 모두 FK 위에 서 있어서 FK 버그가 제어기 버그처럼 보입니다.

## 개념

관절마다 `Rz(q)`가 들어갑니다. 관절을 중심으로 그 각도만큼 도는 회전입니다. link마다 `Tx(l)`이 들어갑니다. link를 따라 그 길이만큼 미끄러지는 이동입니다. 팁 pose는 이들의 순서 있는 곱입니다.

![돌고 한 걸음](../assets/diagram-fk-walk.png)

*base에서 팁까지 번호를 따라가 보세요. 돌고 걷고 돌고 걷습니다.*

길이가 1과 0.5인 link를 생각해 보세요. 어깨를 직각만큼 위로 돌리고 팔꿈치를 반대 방향으로 직각만큼 돌립니다. link 1은 (0, 1)에서 끝나고 link 2는 다시 앞을 향해 (0.5, 0)을 더하므로 팁은 (0.5, 1)에 놓입니다.

어깨가 아래팔도 함께 돌렸다는 것을 잊으면 팁을 (0, 0.5)에 놓게 됩니다.

![팔이 어깨를 돌리고 이어서 팔꿈치를 돌립니다](../assets/clip-example.mp4)

*주황 공을 보세요. 어깨가 팔 전체를 위로 들고 이어서 팔꿈치가 아래팔을 앞으로 접습니다. 빨간 공은 어깨의 회전을 잊은 답입니다.*

평면 사슬의 교차 검증입니다. 관절각의 누적합이 각 link의 방향을 주고 link의 걸음을 더하면 같은 팁이 나옵니다. 팁은 팔을 곧게 폈을 때 base에서 가장 멉니다(link 길이의 합).

팔을 접으면 가장 가깝습니다. 가장 긴 link는 나머지 link만 상쇄할 수 있어서 가장 가까운 거리는 정확히 `max(0, 2*longest - sum)`입니다.

![팁이 base로 돌아올 수 있는 경우](../assets/diagram-reach-bounds.png)

*두 줄을 비교해 보세요. 가장 긴 link가 나머지를 모두 합친 것보다 길면 작업 공간(팁이 닿을 수 있는 모든 곳) 가운데에 구멍이 생깁니다.*

![작업 공간 표본](../assets/fig-workspace.png)

*예측과 맞는지 확인해 보세요. 팔마다 무작위 자세 3,000개입니다. 왼쪽 link [1, 1]은 원판 전체를 덮습니다. 오른쪽 link [3, 1]은 2 m보다 가까이 오지 못합니다.*

## 만들기

```python
def fk_planar(lengths, angles):
    heading = np.cumsum(angles)
    return np.sum(lengths*np.cos(heading)), np.sum(lengths*np.sin(heading)), heading[-1]

def fk_chain(angles, lengths):
    T = np.eye(4)
    for q, l in zip(angles, lengths):
        T = T @ _rz(q) @ _tx(l)
    return T
```

테스트 하나가 두 구현을 무작위 자세에서 돌려 1e-12 이내로 일치하는지 확인합니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/01-math-foundations/02-forward-kinematics -q
```

## 실제 도구로 보기

실제 팔은 Denavit-Hartenberg 매개변수(link를 적는 표준 표)나 URDF joint origin(로봇 파일 속 오프셋)을 쓰고 모든 축이 `z`는 아닙니다. 구조는 같습니다.

link마다 고정 transform 하나와 관절 transform 하나가 붙습니다. FK를 믿기 전에 URDF `<origin>`을 읽고 각각이 어느 frame 기준인지 물어보세요.

출처: Craig, *Introduction to Robotics*, 3판, 3장(매니퓰레이터 기구학).

## 결과물

`outputs/skill-fk-check.md`는 어떤 FK 코드든 구현 두 개로 교차 검증하게 해 줍니다.

## 연습 문제

1. 관절 2를 `y`축 회전으로 바꾸고 평면 테스트가 왜 실패하는지 확인하세요.
2. 두 link 팔의 길이 비에 대해 최소 reach를 그려 보세요.
3. link [1, 1]에서 팁이 base로 돌아오는 자세를 찾으세요.
