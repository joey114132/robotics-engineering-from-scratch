# 2링크 팔의 역기구학

> 한 점에 닿는 문제는 답이 둘이고 한계선이 있는 삼각형입니다. 모든 답은 FK로 검사합니다.

**유형:** 만들기   **선수 지식:** 01/02 순기구학, 02/01 DH 표와 URDF origin   **시간:** 약 15분

## 쉽게 말하면

작업대 위 로봇 팔은 link가 두 개이고 손이 공에 닿아야 해요. base와 팔꿈치와 공이 삼각형을 이뤄요. 두 변은 길이가 정해진 link이고 나머지 한 변은 base에서 공까지 곧게 이은 선이에요.
팔꿈치는 그 선의 양쪽 어느 쪽에든 놓일 수 있어서 공에 닿는 방법이 두 가지예요.

공을 바깥으로 밀면 그 변이 길어지다가 팔이 쭉 펴져요. 그보다 멀면 어떤 방법으로도 닿지 않아요. inverse kinematics(IK)는 목표에 맞는 joint 각도를 구하고 forward kinematics(FK)는 그 각도를 확인해요.

## 문제

팔에게 한 점을 건드리라고 했는데 `acos`(역코사인)가 `nan`(숫자가 아님)을 돌려주거나 팔이 엉뚱한 방향으로 접혀 책상에 부딪힙니다. 완전히 뻗은 길이를 조금 넘는 목표는 쉽게 만들어집니다. 그것을 숨기는 solver는 팔을 엉뚱한 곳으로 보냅니다.

## 개념

첫 그림은 풀이 단계를 나열합니다. `q1`은 x축에서 잰 어깨 각도입니다. `q2`는 팔꿈치 각도이고 팔이 곧게 펴졌을 때 0입니다.

![삼각형으로 푸는 IK](../assets/diagram-triangle.png)

*변이 L1, L2, r인 삼각형입니다. 코사인 법칙(세 변에서 각도를 구하는 규칙)이 q2의 크기를 알려 줍니다.*

코사인 법칙은 `cos q2 = (r² - L1² - L2²) / (2 L1 L2)`를 줍니다. `q2`의 부호는 자유롭게 고릅니다. 양수면 elbow down(팔꿈치가 아래)이고 음수면 elbow up(팔꿈치가 위)입니다.
목표 하나에 닿는 팔이 둘이고 완전히 뻗으면 하나로 합쳐집니다(Craig 4장).

![도달 검사와 FK 검사](../assets/diagram-decision.png)

*`|L1 - L2|`에서 `L1 + L2`까지의 띠 밖에 있는 목표는 거부합니다. 모든 답은 FK로 확인합니다.*

바깥 경계는 완전히 뻗은 상태입니다. 안쪽 경계에서는 팔이 완전히 접히므로 base에서 0.05 m 떨어진 목표도 거부합니다.

![두 elbow와 도달 한계](../assets/fig-two-elbows.png)

*왼쪽은 두 팔이 모두 목표에 닿는 모습입니다. 오른쪽은 두 해가 바깥 경계에서 만나고 그 너머에는 답이 없는 모습입니다.*

0.5 m, 0.4 m 팔에서 목표 (0.6, 0.3) m를 잡습니다. `r = 0.67` m이고 `cos q2 = (0.45 - 0.25 - 0.16)
/ 0.4 = 0.1`이므로 `q2`는 elbow down이면 1.47 rad(84°)이고 elbow up이면 `-1.47` rad입니다.
목표를 같은 `r`로 base 둘레를 돌려 보세요. 삼각형 모양이 그대로여서 `q1`만 따라 움직입니다. 길이가 변하지 않는 검은 선을 보세요.

![원을 도는 목표를 따라가는 elbow](../assets/clip-example.mp4)

*파랑은 elbow down이고 초록은 elbow up입니다. 목표가 0.67 m로 원을 돌아도 `q2`는 ±1.47 rad로 유지됩니다.*

## 만들기

코사인 법칙을 먼저 쓰고 목표 방향 각도에서 삼각형의 안쪽 각도를 뺍니다.

```python
c2 = (x*x + y*y - l1*l1 - l2*l2) / (2*l1*l2)
if abs(c2) > 1 + tol: raise ValueError("unreachable")
s2 = np.sqrt(1 - c2*c2) * (1 if elbow == "down" else -1)
q2 = np.arctan2(s2, c2)
q1 = np.arctan2(y, x) - np.arctan2(l2*s2, l1 + l2*c2)
```

작은 tolerance는 경계에서 반올림 잡음이 가짜 거부로 바뀌는 것을 막습니다. 테스트는 elbow마다 목표 200개에 `fk(ik(p))`를 돌립니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/02-inverse-kinematics-2link -q
python3 phases/02-manipulator-kinematics/02-inverse-kinematics-2link/code/main.py
```

## 실제 도구로 보기

joint가 더 많은 팔은 수치 solver를 씁니다. 2링크 모델에서 이 해석해와 비교하고 solver가 도달 불가 목표를 도달 불가라고 알리는지 확인하세요.

## 결과물

`outputs/skill-ik-answer-check.md`는 IK 답이 controller에 가기 전에 통과해야 하는 검사입니다.

## 연습 문제

1. joint 한계 `|q2| < 2.8`을 넣고 한쪽 elbow가 범위를 벗어나면 `ik`가 다른 쪽을 고르게 하세요.
2. 도달 가능한 띠 전체를 유효한 답의 개수로 칠한 heat map으로 그리세요.
3. `L1 = L2`이고 목표가 base일 때 `q1`이 어떻게 되는지 보이세요.
