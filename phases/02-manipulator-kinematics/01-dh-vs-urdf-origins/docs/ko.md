# DH 표와 URDF origin

> 같은 팔을 DH 표로도 joint origin으로도 적을 수 있고 표를 잘못된 DH convention에 넣으면 에러 없이 틀린 pose가 나옵니다.

**유형:** 만들기   **선수 지식:** 01/02 순기구학   **시간:** 약 15분

## 쉽게 말하면

놀이터에서 방향을 바꾸고 걷는 것과 걸은 뒤 방향을 바꾸는 것은 도착점이 달라질 수 있어요. 방향을 바꾸지 않는 경우만 보면 순서가 달라도 맞아 보여요.

DH convention도 고정 offset과 joint 회전을 적용하는 순서가 달라요. 다른 convention의 표를 쓰려면 먼저 변환해야 해요. 쭉 편 자세만 맞는다고 같은 팔은 아니에요.
구부린 자세도 비교해야 순서 차이로 생긴 오류가 드러나요.

## 문제

교재의 DH 표를 kinematics 코드에 그대로 옮겼습니다. zero pose가 맞아 보여서 넘어갔습니다. 몇 주 뒤 다른 모든 pose에서 팔이 엉뚱한 점에 도달하는데 그동안 에러는 한 번도 나지 않았습니다.

## 개념

![한 팔의 세 가지 표기](../assets/diagram-three-ways.png)

*DH 표, 다른 convention의 DH 표, URDF 식 origin은 같은 팔을 적고 같은 FK를 냅니다.*

Craig의 convention(3장 3.4절)은 `i`행에 `a(i-1)`과 `alpha(i-1)`을 둡니다. 다른 흔한 convention은 `a(i)`와 `alpha(i)`를 둡니다. 그래서 같은 팔도 표가 한 행씩 어긋납니다.

URDF 식 joint는 더 직접적입니다. 부모에서 `xyz` offset과 `rpy` 회전을 준 다음 joint 축으로 돌립니다.

![조용히 틀리는 경로](../assets/diagram-silent-wrong.png)

*두 convention 모두 한 행에 숫자 네 개만 있으면 받아들입니다. 그 표가 다른 convention의 것인지는 알 수 없습니다.*

![틀린 convention과 맞는 convention](../assets/fig-wrong-convention.png)

*왼쪽은 표 하나와 routine 둘이 팔 둘을 만드는 모습입니다. 오른쪽은 오차가 zero pose에서 0이고 거기서부터 커지는 모습입니다.*

## 만들기

각 routine은 한 행마다 기본 변환 네 개를 곱합니다.

```python
def dh_craig(a, alpha, d, th):    return rx(alpha) @ tr(a,0,0) @ rz(th) @ tr(0,0,d)
def dh_standard(a, alpha, d, th): return rz(th) @ tr(0,0,d) @ tr(a,0,0) @ rx(alpha)
```

`craig_to_standard()`는 `(a, alpha)`를 한 행 위로 옮기고 첫 쌍을 base transform으로 남깁니다. `craig_to_urdf()`는 `d`를 origin에 넣고 theta offset이 버려질 상황이면 예외를 냅니다.

```bash
cd robotics-engineering-from-scratch
python3 -m pytest phases/02-manipulator-kinematics/01-dh-vs-urdf-origins -q
python3 phases/02-manipulator-kinematics/01-dh-vs-urdf-origins/code/main.py
```

## 실제 도구로 보기

URDF loader나 MuJoCo 모델은 origin을 읽습니다. 그래서 datasheet의 DH 표는 변환한 다음에 써야 합니다. 변환한 모델의 tip pose를 내 DH 코드와 무작위 pose 다섯 곳에서 비교하세요. zero pose 한 곳만 비교하면 안 됩니다.

## 결과물

`outputs/skill-dh-convention-check.md`는 직접 유도하지 않은 DH 표를 받았을 때 쓰는 점검표입니다.

## 연습 문제

1. `Rx(alpha) Rz(offset)`을 roll, pitch, yaw로 바꿔서 `craig_to_urdf()`에 theta offset을 지원하세요.
2. 틀린 convention이 우연히 다시 맞는 pose를 찾고 이유를 설명하세요.
3. 측정한 tip 위치 두 개로 convention 불일치를 찾아내는 검사를 쓰세요.
